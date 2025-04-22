{pkgs}: {
  deps = [
    pkgs.unzip
    pkgs.libiconv
    pkgs.jq
    pkgs.glibcLocales
    pkgs.postgresql
    pkgs.openssl
  ];
}
