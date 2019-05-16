# Setting up Kubernetes Cluster on Raspberry Pis
First install kubeadm on the RPis and your machine.
https://kubernetes.io/docs/setup/independent/install-kubeadm/
```bash
sudo apt-get install -y kubelet=1.13.0-00 kubeadm=1.13.0-00 kubectl=1.13.0-00 kubernetes-cni=0.6.0-0
```

Then run kubeadm to initialize master
```bash
swapoff -a
sudo kubeadm reset

sudo kubeadm init --apiserver-advertise-address <your_interface_ip_if_using_multiple_interfaces>

mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')&env.IPALLOC_RANGE=10.32.0.0/16"
```

### Setup RaspberryPi
```bash
# The output from kubeadm init above
sudo kubeadm join 10.42.0.1:6443 --token l3y4gc.j4vcuf62ur3q3ma2 --discovery-token-ca-cert-hash sha256:209cf90d686d2c7a447ef5e828525188b9ddc34268f2c03c0672f51b26c1cafc
```

If you get x509 errors, update the time on your RaspberryPi
```bash
sudo date -s "Thu May  9 13:15:02 PDT 2019"
```
