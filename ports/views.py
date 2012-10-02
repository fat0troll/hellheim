from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from ports.models import Port, PortForm
from utils.decorators import is_staff
from vms.models import VirtualMachine, VMForm
import datetime
import sys
import paramiko
import scp

@login_required
def ports_index(request):
    ports = Port.objects.all().order_by('vm')
    return render_to_response('ports/index.html', {
        'ports': ports,
    }, context_instance=RequestContext(request))

@is_staff
def add_port(request):
    """
    TODO: make it real!
    """
    user = request.user
    if request.method == "POST":
        form = PortForm(request.POST)
        if form.is_valid():
            if check_add_form(form, user):
                raise Http404()
            new_port = form.save(commit=False)
            new_port.added_by = user
            new_port.save()
            generate_iptables_file()
            apply_iptables()
            return HttpResponseRedirect('/ports')
        else:
            return render_to_response('ports/add.html', {
                'form': form,
            }, context_instance=RequestContext(request))
    else:
        form = PortForm()
        return render_to_response('ports/add.html', {
            'form': form,
        }, context_instance=RequestContext(request))



def generate_iptables_file():
    config = open('/tmp/config', 'w')
    tmp = "#Generated on: "
    tmp1 = str(datetime.datetime.now())
    config.write(tmp + tmp1 + "\n")
    config.write("""
*mangle
:PREROUTING ACCEPT [1243:219882]
:INPUT ACCEPT [572:88572]
:FORWARD ACCEPT [590:109889]
:OUTPUT ACCEPT [486:56993]
:POSTROUTING ACCEPT [1077:166914]
COMMIT
*nat
:PREROUTING ACCEPT [194:34729]
:POSTROUTING ACCEPT [1:60]
:OUTPUT ACCEPT [129:9035]\n""")
    for entry in Port.objects.values():
        config.write("###Added by %s on %s. Comment: %s. Vm: %s\n" % (User.objects.filter(id = entry['added_by_id'])[0].username, entry['last_modified'], entry['comment'], VirtualMachine.objects.filter(id = entry['vm_id'])[0].name))
        config.write("-A PREROUTING -i eth1 -p tcp -m tcp --dport %s -j DNAT --to-destination %s:%s\n" % (entry['number_out'], VirtualMachine.objects.filter(id = entry['vm_id'])[0].ip_addr , entry['number_in']))

    config.write("""
-A POSTROUTING -o eth1 -j MASQUERADE
COMMIT
*filter
:INPUT ACCEPT [572:88572]
:FORWARD ACCEPT [590:109889]
:OUTPUT ACCEPT [486:56993]
COMMIT\n""")

def apply_iptables():
    ssh_client = Ssh_Conn('root', 'cdover', '192.168.1.104')
    ssh_client.connect()
    ssh_client.start_scp()
    #example
    #ssh_client.execute('cp /etc/exports /etc/exports.backup')
    #ssh_client.recieve_scp('/home/sm/', '/etc/exports.backup')

def check_add_form(form, user):
    status = 0
    
    for field in ['number_in', 'number_out']:
        if not form.cleaned_data[field].isdigit():
            print "non digit ports"
            status += 1
        #works strange
        #if not (int(form.cleaned_data[field]) > 0 and int(form.cleaned_data[field] <= 65535)):
        #    print "wrong port range"
        #    status += 1
    
    if Port.objects.filter(number_in = form.cleaned_data['number_in']):
        print "not unique in port"
        status += 1

    if Port.objects.filter(number_out = form.cleaned_data['number_out'], vm = form.cleaned_data['vm']):
        print "not unique number out + vm"
        status += 1

    if not VirtualMachine.objects.filter(name = form.cleaned_data['vm']):
        print "wrong vm name"
        status += 1

    if VirtualMachine.objects.filter(name = form.cleaned_data['vm'])[0].owner != user:
        print "wrong user"
        status += 1

    if status:
        return True
    else:
        return False



@is_staff
def edit_port(request, pid):
    """
    TODO: make it real!
    """
    port = Port
    user = request.user
    try:
        port = Port.objects.get(id=pid)
    except Port.DoesNotExist:
        raise Http404()
    
    
    if request.method == "POST":
        bform = PortForm(request.POST, instance=port)
        #if VirtualMachine.objects.filter(id = Port.objects.filter(id = pid)[0].vm_id)[0].owner != user:
        #    raise Http404()
        if bform.is_valid():            
            port = bform.save()
            port.last_modified = datetime.datetime.now()
            port.save()
            return HttpResponseRedirect('/ports')
        else:
            return render_to_response('ports/edit.html', {
                'form': bform,
            }, context_instance=RequestContext(request))
    else:
        form = PortForm(instance=port)
        return render_to_response('ports/edit.html', {
            'form': form,
        }, context_instance=RequestContext(request))

@is_staff
def delete_port(request, pid):
    """
    TODO: make it real
    """
    user = request.user
    try:
        port = Port.objects.get(id=pid)
    except Port.DoesNotExist:
        raise Http404()
    #print pid
    #print Port.objects.filter(id = pid)[0].vm_id
    #print VirtualMachine.objects.filter(id = Port.objects.filter(id = pid)[0].vm_id)
    if VirtualMachine.objects.filter(id = Port.objects.filter(id = pid)[0].vm_id)[0].owner != user:
        raise Http404()
    port.delete()
    return HttpResponseRedirect('/ports')

class Ssh_Conn:
	def __init__(self, username, password, host, port = 22):
		self.username = username
		self.password = password
		self.host = host
		self.port = port
		self.ssh = paramiko.SSHClient()
		self.ssh.load_system_host_keys()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.connected = False
		self.scp_enabled = False
	def connect(self):
		self.ssh.connect(self.host, username = self.username, password = self.password, port = self.port)
		self.connected = True
	def execute(self, cmd):
		if self.connected:
			self.ssh_stdin, self.ssh_stdout, self.ssh_stderr = self.ssh.exec_command(cmd)
			print self.ssh_stdout
			print self.ssh_stderr
		else:
			print "Not connected"
	def start_scp(self):
		self.scp = scp.SCPClient(self.ssh.get_transport())
		self.scp_enabled = True
	def send_scp(self, path_from, path_to):
		if self.scp_enabled:
			self.scp.put(files = path_from, remote_path = path_to)
		else:
			print "No scp enabled"
	def recieve_scp(self, path_to, path_from):
		if self.scp_enabled:
			self.scp.get(remote_path = path_from, local_path = path_to)
		else:
			print "No scp enabled"		
