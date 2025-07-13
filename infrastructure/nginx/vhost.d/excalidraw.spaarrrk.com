auth_basic "Zone Restreinte";
auth_basic_user_file /etc/nginx/htpasswd/.htpasswd-excalidraw;
