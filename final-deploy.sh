#!/usr/bin/expect -f

set timeout 300
set server "104.248.93.202"
set password "LucyWorld2025!"

puts "🚀 Deploying Lucy World Search..."

spawn ssh -o StrictHostKeyChecking=no root@$server "cd /var/www && git clone https://github.com/frank2889/lucy-world.git lucy-world-search && cd lucy-world-search && chmod +x deploy.sh && ./deploy.sh"

expect "password:"
send "$password\r"

expect {
    "Deployment completed successfully" {
        puts "✅ Success!"
    }
    "lucy.world" {
        puts "✅ Deployment finished!"
    }
    eof {
        puts "✅ Process completed!"
    }
    timeout {
        puts "⚠️ Deployment may still be running..."
    }
}

puts "🌐 Testing website..."
spawn curl -I http://lucy.world
expect eof

puts "🎉 Done! Check https://lucy.world"