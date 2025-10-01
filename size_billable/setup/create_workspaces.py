import frappe

def create_workspaces():
    """Create Size Billable workspaces"""
    
    print("🏢 Creating Size Billable Workspaces...")
    
    # Create Project Manager workspace
    create_project_manager_workspace()
    
    # Create Project User workspace
    create_project_user_workspace()
    
    # Create Customer Portal workspace
    create_customer_workspace()
    
    # Create main Size Billable workspace
    create_main_workspace()
    
    frappe.db.commit()
    print("✅ All workspaces created successfully!")

def create_project_manager_workspace():
    """Create Project Manager workspace"""
    
    if frappe.db.exists("Workspace", "Project Manager"):
        print("   ⚠️  Project Manager workspace exists, updating...")
        workspace = frappe.get_doc("Workspace", "Project Manager")
    else:
        workspace = frappe.new_doc("Workspace")
        workspace.name = "Project Manager"
    
    workspace.update({
        "label": "Project Manager",
        "title": "Project Manager",
        "icon": "octicon octicon-briefcase",
        "public": 1,
        "module": "Size Billable",
        "sequence_id": 10.0,
        "content": '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Project Management Dashboard</b></span>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Project","col":3}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Timesheet","col":3}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"Task","col":3}},{"id":"shortcuts4","type":"shortcut","data":{"shortcut_name":"Timesheet Approval Report","col":3}}]',
        "shortcuts": [
            {"label": "Project", "link_to": "Project", "type": "DocType"},
            {"label": "Timesheet", "link_to": "Timesheet", "type": "DocType"},
            {"label": "Task", "link_to": "Task", "type": "DocType"},
            {"label": "Timesheet Approval Report", "link_to": "Timesheet Approval Report", "type": "Report"}
        ],
        "links": [
            {"label": "Project Management", "type": "Card Break"},
            {"label": "Project", "link_to": "Project", "link_type": "DocType", "type": "Link"},
            {"label": "Task", "link_to": "Task", "link_type": "DocType", "type": "Link"},
            {"label": "Timesheet", "link_to": "Timesheet", "link_type": "DocType", "type": "Link"},
            {"label": "Reports", "type": "Card Break"},
            {"label": "Timesheet Approval Report", "link_to": "Timesheet Approval Report", "link_type": "Report", "type": "Link", "is_query_report": 1}
        ]
    })
    
    workspace.save()
    print("   ✅ Project Manager workspace created/updated")

def create_project_user_workspace():
    """Create Project User workspace"""
    
    if frappe.db.exists("Workspace", "Project User"):
        print("   ⚠️  Project User workspace exists, updating...")
        workspace = frappe.get_doc("Workspace", "Project User")
    else:
        workspace = frappe.new_doc("Workspace")
        workspace.name = "Project User"
    
    workspace.update({
        "label": "Project User",
        "title": "Project User",
        "icon": "octicon octicon-person",
        "public": 1,
        "module": "Size Billable",
        "sequence_id": 11.0,
        "content": '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>My Work Dashboard</b></span>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Timesheet","col":4}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Task","col":4}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"My Timesheet Report","col":4}}]',
        "shortcuts": [
            {"label": "Timesheet", "link_to": "Timesheet", "type": "DocType"},
            {"label": "Task", "link_to": "Task", "type": "DocType"},
            {"label": "My Timesheet Report", "link_to": "My Timesheet Report", "type": "Report"}
        ],
        "links": [
            {"label": "My Work", "type": "Card Break"},
            {"label": "Timesheet", "link_to": "Timesheet", "link_type": "DocType", "type": "Link"},
            {"label": "Task", "link_to": "Task", "link_type": "DocType", "type": "Link"},
            {"label": "Reports", "type": "Card Break"},
            {"label": "My Timesheet Report", "link_to": "My Timesheet Report", "link_type": "Report", "type": "Link", "is_query_report": 1}
        ]
    })
    
    workspace.save()
    print("   ✅ Project User workspace created/updated")

def create_customer_workspace():
    """Create Customer Portal workspace"""
    
    if frappe.db.exists("Workspace", "Customer Portal"):
        print("   ⚠️  Customer Portal workspace exists, updating...")
        workspace = frappe.get_doc("Workspace", "Customer Portal")
    else:
        workspace = frappe.new_doc("Workspace")
        workspace.name = "Customer Portal"
    
    workspace.update({
        "label": "Customer Portal",
        "title": "Customer Portal",
        "icon": "octicon octicon-globe",
        "public": 1,
        "module": "Size Billable",
        "sequence_id": 12.0,
        "content": '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Customer Portal Dashboard</b></span>","col":12}},{"id":"info1","type":"text","data":{"text":"<p>Welcome to the Customer Portal. Here you can view your project status, billing information, and reports.</p>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Customer Portal","col":6}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Customer Billing Report","col":6}}]',
        "shortcuts": [
            {"label": "Customer Portal", "link_to": "customer-portal", "type": "Page"},
            {"label": "Customer Billing Report", "link_to": "Customer Billing Report", "type": "Report"}
        ],
        "links": [
            {"label": "Customer Portal", "type": "Card Break"},
            {"label": "Customer Portal", "link_to": "customer-portal", "link_type": "Page", "type": "Link"},
            {"label": "Reports", "type": "Card Break"},
            {"label": "Customer Billing Report", "link_to": "Customer Billing Report", "link_type": "Report", "type": "Link", "is_query_report": 1}
        ]
    })
    
    workspace.save()
    print("   ✅ Customer Portal workspace created/updated")

def create_main_workspace():
    """Create main Size Billable workspace"""
    
    if frappe.db.exists("Workspace", "Size Billable"):
        print("   ⚠️  Size Billable workspace exists, updating...")
        workspace = frappe.get_doc("Workspace", "Size Billable")
    else:
        workspace = frappe.new_doc("Workspace")
        workspace.name = "Size Billable"
    
    workspace.update({
        "label": "Size Billable",
        "title": "Size Billable",
        "icon": "octicon octicon-briefcase",
        "public": 1,
        "module": "Size Billable",
        "sequence_id": 9.0,
        "content": '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Size Billable - Enhanced Billing & Timesheet Management</b></span>","col":12}},{"id":"info1","type":"text","data":{"text":"<p>Welcome to Size Billable! This enhanced system provides comprehensive project management, timesheet tracking, and billing capabilities.</p>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Project","col":3}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Timesheet","col":3}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"Task","col":3}},{"id":"shortcuts4","type":"shortcut","data":{"shortcut_name":"Timesheet Approval Report","col":3}}]',
        "shortcuts": [
            {"label": "Project", "link_to": "Project", "type": "DocType"},
            {"label": "Timesheet", "link_to": "Timesheet", "type": "DocType"},
            {"label": "Task", "link_to": "Task", "type": "DocType"},
            {"label": "Timesheet Approval Report", "link_to": "Timesheet Approval Report", "type": "Report"}
        ],
        "links": [
            {"label": "Project Management", "type": "Card Break"},
            {"label": "Project", "link_to": "Project", "link_type": "DocType", "type": "Link"},
            {"label": "Task", "link_to": "Task", "link_type": "DocType", "type": "Link"},
            {"label": "Timesheet", "link_to": "Timesheet", "link_type": "DocType", "type": "Link"},
            {"label": "Reports", "type": "Card Break"},
            {"label": "Timesheet Approval Report", "link_to": "Timesheet Approval Report", "link_type": "Report", "type": "Link", "is_query_report": 1}
        ]
    })
    
    workspace.save()
    print("   ✅ Size Billable workspace created/updated")
