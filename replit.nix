{pkgs}: {
  deps = [
    pkgs.nodePackages.prettier
    pkgs.unzip
    pkgs.libiconv
    pkgs.jq
    pkgs.glibcLocales
    pkgs.postgresql
    pkgs.openssl
  ];
}
