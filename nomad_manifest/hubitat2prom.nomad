job "hubitat2prom" {
  affinity {
    attribute = "${attr.cpu.arch}"
    value = "amd64"
    weight = 100
  }
  datacenters = ["<NOMAD DATACENTRE>"]
  type = "service"
  update {
    max_parallel = 1
    min_healthy_time = "10s"
    healthy_deadline = "3m"
    progress_deadline = "10m"
    auto_revert = false
    canary = 0
  }
  migrate {
    max_parallel = 1
    health_check = "checks"
    min_healthy_time = "10s"
    healthy_deadline = "5m"
  }
  group "hubitat2prom" {
    count = 1
    restart {
      attempts = 20
      interval = "10m"
      delay = "15s"
      mode = "delay"
    }
    ephemeral_disk {
      size = 500
    }
    network {
      mode = "host"
      port "hubitat2prom" {
        to = 5000
      }
    }

    task "hubitat2prom" {
      driver = "docker"
      config {
        image = "proffalken/hubitat2prom:latest"
        volumes = [
            "/media/hubitat2prom/config:/app/config:ro",
            "/etc/localtime:/etc/localtime:ro",
        ]
        ports = ["hubitat2prom"]
      }
      resources {
        cpu    = 400 # 500 MHz
        memory = 512 # 1G
      }
      service {
        name = "hubitat2prom"
        tags = ["hubitat2prom"]
        port = "hubitat2prom"
        check {
          name     = "alive"
          type     = "tcp"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
