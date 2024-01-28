
Reverse engineered obsidian sync server (NOT OFFICIAL).

This project is a duplication of https://github.com/acheong08/obi-sync.<br>
As I lack experience with Go, so I spent two days rewriting it in Python.<br>
Many thanks to [acheong08](https://github.com/acheong08) for the contributions to Obsidian's reverse engineering !

Currently, only some basic features are available. 
As this was completed in haste with my limited experience and without thorough testing, 
there may be many behaviors that are unexpected.

## Features
- End to end encryption
- Live sync (across devices)
- File history/recovery

Support 1.4.16(Windows and Android has been tested)



### Nginx Example
```
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://127.0.0.1:6666;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```

## TODO:

- [ ] fix bug
- [ ] optimize publish

