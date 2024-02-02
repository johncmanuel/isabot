# References: 
# https://nix.libdb.so/slides
# https://github.com/acmcsufoss/api.acmcsuf.com/blob/wip/shell.nix

{ sysPkgs ? import <nixpkgs> {} }:

let
	pkgs = import (sysPkgs.fetchFromGitHub {
		owner = "NixOS";
		repo = "nixpkgs";
		# most recent commit as of 11/13/23
		rev = "bb142a6838c823a2cd8235e1d0dd3641e7dcfd63";
		hash = "sha256:0nbicig1zps3sbk7krhznay73nxr049hgpwyl57qnrbb0byzq9iy";
	}) {};

in pkgs.mkShell {
	buildInputs = with pkgs; [
        python39
        poetry
	];
    shellHook = ''
        poetry env use 3.9
        poetry install
    '';
	# Solves the "libstdc++ not found" issue
	# Reference:
	# https://discourse.nixos.org/t/how-to-solve-libstdc-not-found-in-shell-nix/25458/9
	LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
}

