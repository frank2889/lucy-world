from __future__ import annotations

import secrets
import re
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, FrozenSet, Optional

from sqlalchemy import func

from .extensions import db
from .utils import to_utc_isoformat, utcnow


TRIAL_DURATION_DAYS = 14


@dataclass(frozen=True)
class PlanConfig:
    slug: str
    name: str
    max_daily_queries: int | None
    allowed_providers: tuple[str, ...] | None
    feature_flags: FrozenSet[str]
    description: str = ""


PLAN_CONFIGS: dict[str, PlanConfig] = {
    'trial': PlanConfig(
        slug='trial',
        name='Free Trial',
        max_daily_queries=20,
        allowed_providers=('google',),
        feature_flags=frozenset({'free_search'}),
        description='14-day free trial with Google suggestions only.',
    ),
    'trial_expired': PlanConfig(
        slug='trial_expired',
        name='Trial Expired',
        max_daily_queries=0,
        allowed_providers=(),
        feature_flags=frozenset(),
        description='Trial is over; upgrade required for further usage.',
    ),
    'pro': PlanConfig(
        slug='pro',
        name='Pro',
        max_daily_queries=1000,
        allowed_providers=None,
        feature_flags=frozenset({'free_search', 'premium', 'advanced', 'exports', 'projects'}),
        description='Paid Pro plan with full provider access and productivity features.',
    ),
    'enterprise': PlanConfig(
        slug='enterprise',
        name='Enterprise',
        max_daily_queries=None,
        allowed_providers=None,
        feature_flags=frozenset({'free_search', 'premium', 'advanced', 'exports', 'projects', 'api'}),
        description='Custom enterprise contract with unlimited usage and advanced features.',
    ),
    'public': PlanConfig(
        slug='public',
        name='Public Anonymous',
        max_daily_queries=5,
        allowed_providers=('google',),
        feature_flags=frozenset({'free_search'}),
        description='Unauthenticated access with minimal quota.',
    ),
}


def get_plan_config(slug: str | None) -> PlanConfig:
    key = (slug or 'trial').strip().lower()
    return PLAN_CONFIGS.get(key, PLAN_CONFIGS['trial'])


def effective_plan_slug(plan: str | None, plan_started_at: Optional[datetime]) -> str:
    base_slug = (plan or 'trial').strip().lower()
    if base_slug not in PLAN_CONFIGS:
        base_slug = 'trial'
    if base_slug == 'trial':
        started = plan_started_at or utcnow()
        if utcnow() >= started + timedelta(days=TRIAL_DURATION_DAYS):
            return 'trial_expired'
    return base_slug


def calculate_trial_expiry(plan_started_at: Optional[datetime], fallback: Optional[datetime] = None) -> Optional[datetime]:
    anchor = plan_started_at or fallback
    if not anchor:
        return None
    return anchor + timedelta(days=TRIAL_DURATION_DAYS)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    api_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    plan = db.Column(db.String(32), nullable=False, default='trial', index=True)
    plan_started_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    plan_metadata = db.Column(db.JSON, nullable=True)
    stripe_customer_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    stripe_subscription_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    billing_name = db.Column(db.String(255), nullable=True)
    billing_company = db.Column(db.String(255), nullable=True)
    billing_address_line1 = db.Column(db.String(255), nullable=True)
    billing_address_line2 = db.Column(db.String(255), nullable=True)
    billing_postal_code = db.Column(db.String(32), nullable=True)
    billing_city = db.Column(db.String(128), nullable=True)
    billing_region = db.Column(db.String(128), nullable=True)
    billing_country = db.Column(db.String(2), nullable=True, index=True)
    billing_tax_id = db.Column(db.String(64), nullable=True)

    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    usage_counters = db.relationship('DailyUsage', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def create(email: str, name: Optional[str] = None) -> 'User':
        token = secrets.token_hex(24)
        now = utcnow()
        user = User(
            email=email.strip().lower(),
            name=name,
            api_token=token,
            plan='trial',
            plan_started_at=now,
            plan_metadata={
                'tier': 'free',
                'ai_credits': 0,
            },
        )
        db.session.add(user)
        db.session.commit()
        return user

    def current_plan_slug(self) -> str:
        return effective_plan_slug(self.plan, self.plan_started_at)

    @property
    def plan_config(self) -> PlanConfig:
        return get_plan_config(self.current_plan_slug())

    def trial_expires_at(self) -> Optional[datetime]:
        if self.current_plan_slug() != 'trial':
            return calculate_trial_expiry(self.plan_started_at, self.created_at)
        return calculate_trial_expiry(self.plan_started_at, self.created_at)

    def trial_days_remaining(self) -> int:
        if self.current_plan_slug() != 'trial':
            return 0
        expiry = calculate_trial_expiry(self.plan_started_at, self.created_at)
        if not expiry:
            return 0
        remaining = expiry - utcnow()
        if remaining.total_seconds() <= 0:
            return 0
        days = remaining.days
        if remaining.seconds or remaining.microseconds:
            days += 1
        return max(days, 0)

    def plan_payload(self, *, include_usage: bool = False, queries_used_today: int = 0) -> dict:
        config = self.plan_config
        payload: dict[str, object] = {
            'slug': config.slug,
            'name': config.name,
            'max_daily_queries': config.max_daily_queries,
            'feature_flags': sorted(config.feature_flags),
            'description': config.description,
        }
        if config.allowed_providers is not None:
            payload['allowed_providers'] = list(config.allowed_providers)
        if config.slug == 'trial':
            expiry = calculate_trial_expiry(self.plan_started_at, self.created_at)
            if expiry:
                payload['trial_expires_at'] = to_utc_isoformat(expiry)
                payload['trial_days_remaining'] = self.trial_days_remaining()
        if config.slug == 'trial_expired':
            expiry = calculate_trial_expiry(self.plan_started_at, self.created_at)
            if expiry:
                payload['trial_expired_at'] = to_utc_isoformat(expiry)
            payload['trial_expired'] = True
        if isinstance(self.plan_metadata, dict) and self.plan_metadata:
            payload['metadata'] = self.plan_metadata
        if include_usage:
            payload['queries_used_today'] = queries_used_today
            if config.max_daily_queries is not None:
                payload['queries_remaining_today'] = max(config.max_daily_queries - queries_used_today, 0)
        return payload

    def has_feature(self, feature: str) -> bool:
        return feature in self.plan_config.feature_flags


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(8), nullable=True)
    country = db.Column(db.String(2), nullable=True)
    data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    @staticmethod
    def create(user: User, name: str, description: Optional[str] = None, language: Optional[str] = None, country: Optional[str] = None, data: Optional[dict] = None) -> 'Project':
        proj = Project(user_id=user.id, name=name, description=description, language=language, country=country, data=data or {})
        db.session.add(proj)
        db.session.commit()
        return proj


class LoginToken(db.Model):
    __tablename__ = 'login_tokens'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, nullable=False)
    token = db.Column(db.String(128), unique=True, index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)


class QueryLog(db.Model):
    __tablename__ = 'query_logs'

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    language = db.Column(db.String(8), nullable=True, index=True)
    country = db.Column(db.String(2), nullable=True, index=True)
    providers_queried = db.Column(db.Integer, nullable=False, default=0)
    unique_suggestions = db.Column(db.Integer, nullable=False, default=0)
    total_suggestions = db.Column(db.Integer, nullable=False, default=0)
    audience_score = db.Column(db.Float, nullable=False, default=0.0)
    context_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    passes_threshold = db.Column(db.Boolean, default=False, nullable=False, index=True)
    threshold_reason = db.Column(db.String(128), nullable=True)

    candidate = db.relationship('CandidateQuery', backref='log', uselist=False)

    @staticmethod
    def record(
        *,
        keyword: str,
        language: Optional[str],
        country: Optional[str],
        providers_queried: int,
        unique_suggestions: int,
        total_suggestions: int,
        audience_score: float,
        passes_threshold: bool,
        threshold_reason: Optional[str],
        metadata: Optional[dict] = None,
    ) -> "QueryLog":
        entry = QueryLog(
            keyword=keyword,
            language=language,
            country=country,
            providers_queried=providers_queried,
            unique_suggestions=unique_suggestions,
            total_suggestions=total_suggestions,
            audience_score=audience_score,
            passes_threshold=passes_threshold,
            threshold_reason=threshold_reason,
            context_json=metadata,
        )
        db.session.add(entry)
        db.session.commit()
        return entry


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    processor = db.Column(db.String(32), nullable=False)
    order_id = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    net_amount = db.Column(db.Numeric(10, 2), nullable=True)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(3), nullable=False)
    payer_email = db.Column(db.String(255), nullable=True)
    metadata_payload = db.Column('metadata', db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    invoice_number = db.Column(db.String(64), nullable=True, unique=True)
    invoice_path = db.Column(db.String(255), nullable=True)

    @property
    def amount_decimal(self) -> Decimal:
        return Decimal(str(self.amount or '0'))

    @property
    def net_amount_decimal(self) -> Decimal:
        if self.net_amount is None:
            return self.amount_decimal
        return Decimal(str(self.net_amount))

    @property
    def tax_amount_decimal(self) -> Decimal:
        if self.tax_amount is None:
            return Decimal('0')
        return Decimal(str(self.tax_amount))

    def metadata_dict(self) -> dict[str, Any]:
        payload = self.metadata_payload
        if isinstance(payload, dict):
            return payload
        return {}


class CandidateQuery(db.Model):
    __tablename__ = 'candidate_queries'

    id = db.Column(db.Integer, primary_key=True)
    query_log_id = db.Column(db.Integer, db.ForeignKey('query_logs.id'), nullable=False, unique=True)
    keyword = db.Column(db.String(255), nullable=False, index=True)
    language = db.Column(db.String(8), nullable=True, index=True)
    country = db.Column(db.String(2), nullable=True, index=True)
    audience_score = db.Column(db.Float, nullable=False, default=0.0)
    threshold_reason = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(32), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False, index=True)

    drafts = db.relationship('ContentDraft', backref='candidate', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def ensure_from_log(log: QueryLog, reason: Optional[str]) -> "CandidateQuery":
        candidate = CandidateQuery.query.filter_by(
            keyword=log.keyword,
            language=log.language,
            country=log.country,
        ).one_or_none()

        if candidate:
            candidate.query_log_id = log.id
            candidate.audience_score = log.audience_score
            candidate.threshold_reason = reason
            # Only reset status for dormant candidates; keep published or active states intact
            if candidate.status in {'failed', 'archived'}:
                candidate.status = 'pending'
        else:
            candidate = CandidateQuery(
                query_log_id=log.id,
                keyword=log.keyword,
                language=log.language,
                country=log.country,
                audience_score=log.audience_score,
                threshold_reason=reason,
                status='pending',
            )
            db.session.add(candidate)

        db.session.commit()
        return candidate


class ContentDraft(db.Model):
    __tablename__ = 'content_drafts'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_queries.id'), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    outline = db.Column(db.JSON, nullable=True)
    markdown = db.Column(db.Text, nullable=False)
    html = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(8), nullable=True, index=True)
    country = db.Column(db.String(2), nullable=True, index=True)
    author_name = db.Column(db.String(128), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(32), nullable=False, default='draft', index=True)
    created_at = db.Column(db.DateTime, default=utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow, nullable=False, index=True)
    published_at = db.Column(db.DateTime, nullable=True, index=True)

    @staticmethod
    def next_slug(base_slug: str) -> str:
        base = re.sub(r'[^a-z0-9]+', '-', base_slug.lower()).strip('-') or 'post'
        slug = base
        counter = 2
        while ContentDraft.query.filter(func.lower(ContentDraft.slug) == slug.lower()).first():
            slug = f"{base}-{counter}"
            counter += 1
        return slug


class DailyUsage(db.Model):
    __tablename__ = 'daily_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    query_count = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='uq_daily_usage_user_date'),)

    @staticmethod
    def for_day(user: 'User', day: date) -> 'DailyUsage | None':
        return DailyUsage.query.filter_by(user_id=user.id, date=day).first()

    @staticmethod
    def touch(user: 'User', day: date) -> 'DailyUsage':
        usage = DailyUsage.for_day(user, day)
        if usage is None:
            usage = DailyUsage(user_id=user.id, date=day, query_count=0)
            db.session.add(usage)
        return usage


