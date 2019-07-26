#!/usr/bin/python
# (c) 2019, Whitney Champion <whitney.ellis.champion@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
module: jira_search
short_description: Communicate with jira to provide issue searching capabality
description:
    - Search Jira API for issues
version_added: "1.0"
author: "Adam Corriveau (@livemonkey1300)"
options:
  uri:
    description:
      - domain of the compagny
    required: true
    default: None
  username:
    description:
      - Username having permission to the current filter
    required: true
    default: None
  password:
    description:
      - Password of the current user for jira api access
    required: true
    default: None
  filter:
    description:
      - The filter id to the issue search
    required: false
    default: 4
"""

EXAMPLES = '''
# Get Jira Issue
- name: Get Jira Issue
  jira_search:
      uri: "{{ domain }}"
      username: "{{ username }}"
      password: "{{ password }}"
  register: issue

# Get Jira Issue using a specific filter
- name: Get Jira Issue
  jira_search:
      uri: "{{ domain }}"
      username: "{{ username }}"
      password: "{{ password }}"
      filter: 4
  register: issue

# Example of the issues output
- name: Print Jira Issues
  debug:
    msg: "{{ item.fields }}"
  with_items: "{{ issue.jira.issues }}"
'''

RETURN = r'''
jira:
  description: Return Jira Issues
  returned: always
  type: complex
msg:
  description: Return if theire was an issues
  returned: always
  type: str
  sample: OK (unknown bytes)
changed:
  description: Return change depending on success
  returned: always
  type: int
  sample: 200
'''

import base64
import json
import sys
import requests
from ansible.module_utils._text import to_text, to_bytes

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url



class JiraSearch:
    def __init__(self, host , username , password , filter=4):
        self.host = "https://" + host + "/"
        self.username = username
        self.password = password
        self.auth = base64.b64encode('{0}:{1}'.format(self.username, self.password))
        self.filter = filter
    
    def connect_jira(self , query='search?filter='):
        url = '%s%s%s%s' % ( self.host , "rest/api/2/" , query , self.filter )
        headers = { "Accept": "application/json","Authorization": "Basic %s" % self.auth }
        response = requests.request("GET",url,headers=headers)
        return response

    def get_jira_result(self):
        response = self.connect_jira()
        return json.loads(response.text)

def main():
    global module
    module = AnsibleModule(
        argument_spec = dict(
            uri= dict(required=True),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            filter=dict(type='int', default=4),
        )
    )
    uri = module.params['uri']
    user = module.params['username']
    passwd = module.params['password']
    filter = module.params['filter']

    try:
        jira_con = JiraSearch( uri , user , passwd , filter ).get_jira_result()

    except Exception as e:
        return module.fail_json(changed=False , msg=e.message)

    module.exit_json(changed=True, jira=dict(jira_con))



if __name__ == '__main__':
    main()