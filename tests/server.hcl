listener "tcp" {
  address = "127.0.0.1:8200"
  tls_cert_file = "certs/cert.pem"
  tls_key_file = "certs/key.pem"
}

backend "inmem" {
}
