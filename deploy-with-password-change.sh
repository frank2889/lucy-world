#!/usr/bin/expect -f

# Password change and deployment script
set timeout 60
set server "104.248.93.202"
set old_password "c9d52e7a492b040e7da47ceb1d"
set new_password "LucyWorld2025!"

puts "🔐 Changing server password and deploying..."

# SSH to server
spawn ssh root@$server
expect {
    "password:" {
        send "$old_password\r"
        exp_continue
    }
    "New password:" {
        puts "Setting new password..."
        send "$new_password\r"
        exp_continue
    }
    "Retype new password:" {
        send "$new_password\r"
        exp_continue
    }
    "Connection to * closed" {
        puts "Password changed successfully, reconnecting..."
    }
}

# Reconnect with new password
puts "🔄 Reconnecting with new password..."
spawn ssh root@$server
expect "password:"
send "$new_password\r"
expect "root@"

puts "✅ Connected! Starting deployment..."

# Deploy from GitHub
send "cd /var/www\r"
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
    "root@" {
        puts "✅ Deployment completed!"
    }
    timeout {
        puts "⚠️ Deployment may still be running..."
    }
}

send "exit\r"
expect eof

puts ""
puts "🎉 Deployment finished!"
puts "New server password: $new_password"
puts "Your site should be live at: https://lucy.world"