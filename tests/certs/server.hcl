listener "tcp" {
  address = "127.0.0.1:8201"
  tls_cert_file = "server.crt"
  tls_key_file = "server.key"
}

backend "inmem" {
}
