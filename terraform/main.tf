terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }

  required_version = ">= 1.5.0"
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_deployment_v1" "habitpulse" {
  metadata {
    name = "habitpulse"
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "habitpulse"
      }
    }

    template {
      metadata {
        labels = {
          app = "habitpulse"
        }
      }

      spec {
        container {
          name  = "habitpulse"
          image = "sureshkrishnasp/habitpulse:latest"

          image_pull_policy = "Always"

          port {
            container_port = 5000
          }
        }
      }
    }
  }
}

resource "kubernetes_service_v1" "habitpulse" {
  metadata {
    name = "habitpulse-service"
  }

  spec {
    selector = {
      app = "habitpulse"
    }

    port {
      port        = 5000
      target_port = 5000
    }

    type = "NodePort"
  }
}
