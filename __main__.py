import pulumi
import pulumi_aws as aws

vpc = aws.ec2.Vpc(
    "Vpc-ec2",
    cidr_block = "10.0.0.0/16",
    tags={ 
        "Name" : "VPC-EC2"
    }
    
)

public_subnet = aws.ec2.Subnet(
    "Subnet-public-ec2", 
    cidr_block = "10.0.101.0/24", 
    tags = {
        "Name" : "ec2-public"
    },
    vpc_id=vpc.id
)

internet_gateway = aws.ec2.InternetGateway(
    "Igw-ec2",
    vpc_id=vpc.id
)

route_table = aws.ec2.RouteTable(
    "ec2-route-table",
    vpc_id=vpc.id,
    routes=[
        {
            "cidr_block" : "0.0.0.0/0",
            "gateway_id" : internet_gateway.id
        }
    ]
)
rt_table_assoc = aws.ec2.RouteTableAssociation(
    "ec2-rta",
    route_table_id=route_table.id,
    subnet_id=public_subnet.id
)

group = aws.ec2.SecurityGroup(
    "web-secgrp",
    description="Enable HTTP Access",
    ingress=[
        {
            "protocol": "icmp", "from_port": 8, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],
        },
        {  
            "protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"],
        },
        {  
            "protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    vpc_id=vpc.id
)

instance = aws.ec2.Instance(
    "web=server",
    instance_type="t2.micro",
    vpc_security_group_ids=[group.id],
    ami="ami-0b0dcb5067f052a63",
    user_data=
    """
        #!/bin/bash
        echo "Hello, World!" > index.html
        nohup python -m SimpleHTTPServer 80 &
    """,
    tags={
        "Name": "web-server",
    },
    subnet_id=public_subnet.id,
    associate_public_ip_address=True
)

pulumi.export("ip", instance.public_ip)
pulumi.export("hostname", instance.public_dns)