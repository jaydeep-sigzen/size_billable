import frappe

def fix_workspace_content():
    """Fix empty workspaces by adding content"""
    
    print("🔄 Fixing Size Billable Workspaces Content...")
    
    try:
        # Update Size Billable workspace
        if frappe.db.exists("Workspace", "Size Billable"):
            workspace = frappe.get_doc("Workspace", "Size Billable")
            workspace.content = '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Size Billable - Enhanced Billing & Timesheet Management</b></span>","col":12}},{"id":"info1","type":"text","data":{"text":"<p>Welcome to Size Billable! This enhanced system provides comprehensive project management, timesheet tracking, and billing capabilities.</p>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Project","col":3}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Timesheet","col":3}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"Task","col":3}},{"id":"shortcuts4","type":"shortcut","data":{"shortcut_name":"Timesheet Approval Report","col":3}}]'
            workspace.save()
            print("   ✅ Size Billable workspace updated")
        
        # Update Project Manager workspace
        if frappe.db.exists("Workspace", "Project Manager"):
            workspace = frappe.get_doc("Workspace", "Project Manager")
            workspace.content = '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Project Management Dashboard</b></span>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Project","col":3}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Timesheet","col":3}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"Task","col":3}},{"id":"shortcuts4","type":"shortcut","data":{"shortcut_name":"Timesheet Approval Report","col":3}}]'
        workspace.save()
        
        # Add SB Project Manager role
        workspace.append("roles", {"role": "SB Project Manager"})
        workspace.save()
        
        print("   ✅ Project Manager workspace updated")
        
        # Update Project User workspace
        if frappe.db.exists("Workspace", "Project User"):
            workspace = frappe.get_doc("Workspace", "Project User")
            workspace.content = '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>My Work Dashboard</b></span>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Timesheet","col":4}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Task","col":4}},{"id":"shortcuts3","type":"shortcut","data":{"shortcut_name":"My Timesheet Report","col":4}}]'
            workspace.save()
            print("   ✅ Project User workspace updated")
        
        # Update Customer Portal workspace
        if frappe.db.exists("Workspace", "Customer Portal"):
            workspace = frappe.get_doc("Workspace", "Customer Portal")
            workspace.content = '[{"id":"header1","type":"header","data":{"text":"<span class=\\"h4\\"><b>Customer Portal Dashboard</b></span>","col":12}},{"id":"info1","type":"text","data":{"text":"<p>Welcome to the Customer Portal. Here you can view your project status, billing information, and reports.</p>","col":12}},{"id":"shortcuts1","type":"shortcut","data":{"shortcut_name":"Customer Portal","col":6}},{"id":"shortcuts2","type":"shortcut","data":{"shortcut_name":"Customer Billing Report","col":6}}]'
            workspace.save()
            print("   ✅ Customer Portal workspace updated")
        
        frappe.db.commit()
        print("✅ All workspaces content updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        frappe.log_error(f"Workspace content update error: {e}")
