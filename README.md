# S3 bucket finder from Bind9 dns logs
This will look at bind9 dns query logs and try to find open s3 buckets
## Requirements:
Bind9 as caching server

boto3: pip install boto3

aws cli: pip install awscli 

### AWS
Configure aws with aws configure from cli, add in access keys

## Installing bind9 as cache server
### Ubuntu
#### prerecs
apt-get install bind9 dnsutils
#### configuration
edit /etc/bind/named.conf.options
add the following to the options area in the file
```     
forwarders {
    8.8.8.8;
    8.8.4.4;
    };
```

Now we need to add logging, we can enable all logging or just dns queries

Add the following to the end of named.conf:

`include "/etc/named/named.conf.logging";`

Make a new file `/etc/named/named.conf.logging` and add the following: 


#### all logging
```
logging {
    channel default_file {
        file "/var/log/named/default.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel general_file {
        file "/var/log/named/general.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel database_file {
        file "/var/log/named/database.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel security_file {
        file "/var/log/named/security.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel config_file {
        file "/var/log/named/config.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel resolver_file {
        file "/var/log/named/resolver.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel xfer-in_file {
        file "/var/log/named/xfer-in.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel xfer-out_file {
        file "/var/log/named/xfer-out.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel notify_file {
        file "/var/log/named/notify.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel client_file {
        file "/var/log/named/client.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel unmatched_file {
        file "/var/log/named/unmatched.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel queries_file {
        file "/var/log/named/queries.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel network_file {
        file "/var/log/named/network.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel update_file {
        file "/var/log/named/update.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel dispatch_file {
        file "/var/log/named/dispatch.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel dnssec_file {
        file "/var/log/named/dnssec.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    channel lame-servers_file {
        file "/var/log/named/lame-servers.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };

    category default { default_file; };
    category general { general_file; };
    category database { database_file; };
    category security { security_file; };
    category config { config_file; };
    category resolver { resolver_file; };
    category xfer-in { xfer-in_file; };
    category xfer-out { xfer-out_file; };
    category notify { notify_file; };
    category client { client_file; };
    category unmatched { unmatched_file; };
    category queries { queries_file; };
    category network { network_file; };
    category update { update_file; };
    category dispatch { dispatch_file; };
    category dnssec { dnssec_file; };
    category lame-servers { lame-servers_file; };
}; 
```

#### just DNS queries
```
logging {
    channel queries_file {
        file "/var/log/named/queries.log" versions 3 size 5m;
        severity dynamic;
        print-time yes;
    };
    category queries { queries_file; };
};
```

Next, add logging directory 

```
mkdir /var/log/named
chown bind /var/log/named
```

Now restart the service and check the status: 
```
service bind9 restart
service bind9 status

```

If this returns active / running we need to check that DNS resolves: `nslookup google.com 127.0.0.1`
If all checks clear, change router or computers dns to point at the cache server

###Log rotation:

We will be using logrotate to run the script, after modifying the prerotate to point to the area with the script
add the following to `/etc/logrotate.d/bind`


```
/var/log/named/queries.log {
  daily
  missingok
  rotate 7
  compress
  delaycompress
  create 644 bind bind
  ifempty
  sharedscripts
  prerotate
    python /var/s3/s3_finder.py
  endscript
  postrotate
   service bind9 restart
  endscript
}
```
Testing will be after configuration of tool

## Using
### First run:

edit s3_config.py to point to good areas for database and logs (make absolute paths eg: /var/s3/database.db)
run  `logrotate -f /var/logrotate.d/bind` to test if the script will rotate and execute


