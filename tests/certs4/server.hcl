listener "tcp" {
  address = "127.0.0.1:8200"
  tls_cert_file = "mycert1.cer"
  tls_key_file = "mycert1.key"
}

backend "inmem" {
}
