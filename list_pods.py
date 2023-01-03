import boto3
import os
from flask import Flask, render_template, request, flash
from kubernetes import client, config
import logging
from forms import GetNamespace, GetParameter, UpdateParameter
import logging




log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)

# To override the default severity of logging
logger.setLevel('INFO')

# Use FileHandler() to log to a file
file_handler = logging.StreamHandler()
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)
logger.info("I am a separate Logger")


profile_name = ['Dev']
#logging.info("profile used is", profile_name)
logging.warning("profile used is %profile_name %")

config.load_kube_config()
#config.load_incluster_config()
v1 = client.CoreV1Api()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Test123'

@app.route('/', methods=('GET', 'POST'))
def home():
    return render_template('home.html')

pod_name = []
image_name=[]
status = []
creation_timestamp = []
not_approved_ns = ['default', 'gitlab-managed-apps','kube-public', 'kube-system']
@app.route('/pods', methods=['GET','POST'])
def pods():
    form = GetNamespace()
    if form.validate_on_submit():
        #flash(f'Submitted the namespace {form.pod_namespace.data}', 'Success')
        global namespace_name
        namespace_name = form.pod_namespace.data
        print(namespace_name)
        print(form.pod_namespace.data)
        print(form.user_name.data)
        logger.info(f'Restarted by {form.user_name.data}')
        namespace = form.pod_namespace.data
        ret = v1.list_namespaced_pod(namespace=namespace)
        if namespace in not_approved_ns:
            #print('trying to attempt system namespace')
            logger.info(f'User {form.user_name.data} tried to Access {namespace}!')
            return render_template("notallowed.html")
        else:
            #print(ret.items)
            try:
                #ret = v1.list_namespaced_pod(namespace=namespace)
                #print(type(ret))
                #print(ret.items)
                for i in ret.items:
                    #pods_list.append(i.metadata.image)
                    pod_name.append(i.metadata.name)
                    image_name.append((i.status.container_statuses[0].image).split("/")[-1].split(":")[-1])
                    #print((i.status.container_statuses[0].image).split("/")[-1])
                    #print((i.status.container_statuses[0].image).split("/")[-1]
                    status.append(i.status.phase)
                    #print("creation_timestamp-->", i.metadata.get('creation_timestamp'))
                    #print("creation_timestamp-->", i.metadata.creation_timestamp)
                    creation_timestamp.append(i.metadata.creation_timestamp)

                    #print("%s\t%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name, i.metadata.image))
                return render_template("resultold.html", image_name=image_name, pod_name=pod_name, status=status,creation_timestamp=creation_timestamp)


            except:
                logger.error(f'Error in Getting Namespace Method!')
            #print("Deleted")
    return render_template('pods.html', form=form)

pods_delete_list = []
@app.route('/deletepod', methods=['GET','POST'])
def deletepod():
    if request.method == 'POST':
        print(request.form.getlist('pod-names'))
        pods_delete_list.append(request.form.getlist('pod-names'))
        print("Start of pod deletion")
        logger.info(f'Pod restart Initiated!')
        print("Global Namespace", namespace_name)
        print(pods_delete_list)
        for i in pods_delete_list:
            print("pods list",i)
        try:
            for pod in pods_delete_list[0]:
                #print(v1.delete_namespaced_pod(namespace=namespace_name, name=pod))
                v1.delete_namespaced_pod(namespace=namespace_name, name=pod)
                print("Pod restart Completed!", pod)
                logger.info(f'Pod restart Completed!')
                print("Clearing pods list", status.clear())
                print("Clearing delete list", pod_name.clear())
                print("Clearing Image list", image_name.clear())
                print("clearing timestamp", creation_timestamp.clear())
                print('Removing Deletion list',pods_delete_list.clear())
                logger.info(f'List Cleared')

        except:
            #print("Error IN Deletion")
            logger.error(f'Error in Intiating Restarted Method')
        #
        print("Clearing pods list", status.clear())
        print("Clearing delete list", pod_name.clear())
        print("Clearing Image list", image_name.clear())
        print("clearing timestamp", creation_timestamp.clear())
        print('Removing Deletion list', pods_delete_list.clear())
        return render_template("completed.html")
    return "Process Completed"




boto3.setup_default_session(profile_name='Dev')
client = boto3.client('ssm')
def params(key, value):
    response = client.put_parameter(
        Name=key,
        Type='String',
        Value=value,
        Overwrite=True

    )
def paramsupdate(key):
    response = client.get_parameters(
        Names=[key]
    )
    global param_modified_time
    param_modified_time = response.get('Parameters')[0].get('LastModifiedDate')
    return response.get('Parameters')[0].get('Value')
@app.route('/parametermodify', methods=['GET','POST'])
def parametermodify():
    form = GetParameter()
    if form.validate_on_submit():
        print("Parameter Name",form.parameter_name.data)
        key = form.parameter_name.data
        print('keyyy', key)
        try:
            abc = paramsupdate(key)
            print("modified_time",param_modified_time)
            modified_time = param_modified_time

            logger.info(f'Parameter {form.parameter_name.data} Updated !')
            return render_template("param.html", abc=abc, name=key, modified_time=modified_time)
        except:
            #print("Parameter Update issue")
            logger.error(f'Parameter {form.parameter_name.data} Update Error !')
    return render_template("parametermodify.html", form=form)

@app.route('/parameters', methods=['GET','POST'])
def parameterupdate():
    form = UpdateParameter()
    if form.validate_on_submit():
        #print("Parameter Name",form.parameter_name.data)
        #print("Parameter Key", form.parameter_key.data)
        key = form.parameter_name.data.lstrip() and form.parameter_name.data.rstrip()
        value = form.parameter_key.data.lstrip() and form.parameter_key.data.rstrip()
        try:
            params(key,value)
            #flash(f'Parameter Created {form.parameter_name.data}', 'Success')
            return render_template("completed.html")
        except:
            print("Parameter creation issue")
    return render_template("parameter.html", form=form)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)

