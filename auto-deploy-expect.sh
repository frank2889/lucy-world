#!/usr/bin/expect -f

# Automated deployment script for Lucy World Search
set timeout 300
set server "104.248.93.202"
set password "c9d52e7a492b040e7da47ceb1d"

puts "🚀 Starting automated deployment to $server..."

# SSH to server
spawn ssh root@$server
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    "root@" {
        puts "✅ Connected to server!"
    }
}

# Deploy from GitHub
puts "📦 Cloning from GitHub..."
send "cd /var/www\r"
expect "root@"

send "rm -rf lucy-world-search\r"
expect "root@"

send "git clone https://github.com/frank2889/lucy-world.git lucy-world-search\r"
expect "root@"

send "cd lucy-world-search\r"
expect "root@"

send "chmod +x deploy.sh\r"
expect "root@"

puts "🔧 Running deployment script..."
send "./deploy.sh\r"
expect {
    "completed successfully" {
        puts "✅ Deployment successful!"
    }
    timeout {
        puts "⏰ Deployment taking longer than expected..."
    }
}

# Test the site
puts "🌐 Testing website..."
send "curl -I https://lucy.world/health\r"
expect "root@"

send "exit\r"
expect eof

puts "🎉 Deployment completed!"
puts "Your site should now be live at: https://lucy.world"