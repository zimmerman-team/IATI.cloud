# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.provision "shell", path: "bin/setup/install_dependencies.sh"
  config.vm.provision "shell", path: "bin/setup/install_virtualenv.sh"
  config.vm.provision "shell", path: "bin/setup/create_local_settings.sh"
  config.vm.provision "shell", path: "bin/setup/update_bashrc.sh"
  config.vm.provision "shell", path: "bin/setup/sync_db.sh"

  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 4200, host: 19420

  config.vm.define "oipa" do |oipa|
  end

  config.vm.provider :virtualbox do |vb, override|
    vb.customize ["modifyvm", :id, "--memory", 1542]
  end

end
