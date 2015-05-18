listener "tcp" {
  address = "127.0.0.1:8200"
  tls_cert_file = "foo.crt"
  tls_key_file = "foo.key"
}

backend "inmem" {
}
