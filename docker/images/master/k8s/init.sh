#!/usr/bin/env bash
scriptdir="$(dirname "$0")"
cd "$scriptdir"
kubectl create -f namespace-nomad.json
kubectl create -f make_nomad_sa_admin.yaml