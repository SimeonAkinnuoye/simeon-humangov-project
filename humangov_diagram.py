from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EKS, Lambda, ECR
from diagrams.aws.network import Route53, ALB, VPC, InternetGateway
from diagrams.aws.database import Dynamodb
from diagrams.aws.storage import S3
from diagrams.aws.devtools import Codebuild, Codepipeline
from diagrams.aws.management import Cloudwatch
from diagrams.aws.general import Users
from diagrams.onprem.vcs import Github
from diagrams.saas.chat import Slack
from diagrams.k8s.network import Ingress, Service
from diagrams.k8s.compute import Pod
from diagrams.onprem.client import User

# Create the Diagram
with Diagram("HumanGov AWS Architecture (us-east-1)", show=False, direction="LR"):

    # --- External Actors ---
    users = User("End Users")
    developer = User("Dev Team")
    sre_team = User("SRE Team")
    
    # --- External Tools ---
    github = Github("GitHub Repo")
    slack = Slack("Slack Notifications")

    # --- AWS Cloud Boundary ---
    with Cluster("AWS Cloud (Region: us-east-1)"):
        
        # --- VPC Boundary ---
        with Cluster("VPC (10.0.0.0/16)"):
            
            # 1. CI/CD Components (DevOps)
            with Cluster("CI/CD Pipeline"):
                pipeline = Codepipeline("AWS CodePipeline")
                build = Codebuild("AWS CodeBuild")
                ecr = ECR("Amazon ECR")

            # 2. Data & Serverless Layer
            with Cluster("Data & Serverless"):
                s3 = S3("S3 Bucket\n(Files)")
                dynamo = Dynamodb("DynamoDB\n(State Data)")
                
                # DynamoDB Stream to Lambda
                lambda_func = Lambda("Python Lambda\n(Stream Processor)")
                dynamo >> Edge(label="DDB Stream", color="brown") >> lambda_func

            # 3. Observability
            with Cluster("Observability"):
                cw_syn = Cloudwatch("CloudWatch\nSynthetics")
                cw_alarm = Cloudwatch("CloudWatch\nAlarm")
                cw_syn >> cw_alarm

            # 4. Networking Entry
            r53 = Route53("Amazon Route53")
            alb = ALB("Application\nLoad Balancer")

            # 5. EKS Cluster (Compute)
            with Cluster("Amazon EKS Cluster"):
                
                # Logical Environment
                with Cluster("Namespace: humangov-state"):
                    
                    # Kubernetes Ingress
                    k8s_ingress = Ingress("K8s Ingress")
                    
                    # Grouping Services
                    with Cluster("Services"):
                        svc_nginx = Service("Service Nginx")
                        svc_app = Service("Service App")
                    
                    # Grouping Pods
                    with Cluster("Pods"):
                        pod_nginx = Pod("Pod Nginx")
                        pod_app = Pod("Pod App\n(Microservice)")
                        humangov_pod = Pod("HumanGov Pod")

                    # K8s Internal Wiring
                    k8s_ingress >> svc_nginx >> pod_nginx
                    k8s_ingress >> svc_app >> pod_app
                    svc_app >> humangov_pod

                    # Pods connecting to Data Layer
                    pod_app >> Edge(label="Read/Write") >> dynamo
                    pod_app >> Edge(label="Store") >> s3

    # --- Wiring the Big Picture ---

    # Flow 1: User Access
    users >> Edge(label="DNS Query") >> r53
    r53 >> Edge(label="Traffic") >> alb
    alb >> Edge(label="Forward") >> k8s_ingress

    # Flow 2: Developer CI/CD
    developer >> Edge(label="Git Push") >> github
    github >> Edge(label="Webhook") >> pipeline
    pipeline >> build
    build >> Edge(label="Push Image") >> ecr
    
    # Deployment (ECR to EKS)
    ecr >> Edge(style="dashed", label="Image Pull") >> pod_app

    # Flow 3: SRE & Observability
    # (Assuming Synthetics monitors the ALB endpoint)
    alb >> Edge(style="dotted") >> cw_syn
    cw_alarm >> Edge(label="Alert", color="red") >> slack
    slack >> sre_team