from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Function to create an EC2 instance using Terraform
def create_ec2_instance(ami, instance_type, region):
    try:
        # Set AWS region as an environment variable for Terraform
        os.environ["AWS_DEFAULT_REGION"] = region

        # Create a dynamic Terraform configuration file
        tf_config = f'''
        provider "aws" {{
            region = "{region}"
        }}

        resource "aws_instance" "ec2-instance" {{
            ami           = "{ami}"
            instance_type = "{instance_type}"
            # Add more instance configuration here
        }}
        '''

        # Write the Terraform configuration to a file
        with open("terraform.tf", "w") as tf_file:
            tf_file.write(tf_config)

        # Execute Terraform commands
        subprocess.run(['terraform', 'init'])
        subprocess.run(['terraform', 'apply', '-auto-approve'])

        return True, "EC2 instance provisioning successful!"

    except Exception as e:
        return False, str(e)

# Function to destroy the EC2 instance using Terraform
def destroy_ec2_instance():
    try:
        # Execute Terraform destroy command
        subprocess.run(['terraform', 'destroy', '-auto-approve'])

        return True, "EC2 instance destroyed successfully!"

    except Exception as e:
        return False, str(e)

# API endpoint for creating an EC2 instance
@app.route('/create-ec2', methods=['POST'])
def create_ec2():
    try:
        data = request.json

        # Extract parameters from the JSON request
        ami = data['ami']
        instance_type = data['size']
        region = data['region']

        # Create the EC2 instance using Terraform
        success, message = create_ec2_instance(ami, instance_type, region)

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoint for destroying an EC2 instance
@app.route('/destroy-ec2', methods=['POST'])
def destroy_ec2():
    try:
        # Destroy the EC2 instance using Terraform
        success, message = destroy_ec2_instance()

        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)