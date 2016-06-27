/*
 * Copyright 2016 Deany Dean
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License. 
 */

/**
 * Contains all the javascript for the dnsfilter admin web UI.
 */
var TRUSTED_SITES_UL = "#trusted-sites-list";
var KNOWN_DEVICES_UL = "#known-devices-list";

function ajax_failed(req, status, error)
{
    console.log("Failed ajax request: "+status+" "+error);
}

/**
 * Get all the sites names from the webservice.
 */
function get_sites()
{
    $.ajax("/sites", {
        dataType: "json"       
    }).done(init_sites_list);
}

/**
 * Get all the known devices from the webservice
 */
function get_devices()
{
    $.ajax("/devices", {
        dataType: "json"
    }).done(init_device_list).fail(ajax_failed);
}

/**
 * Add a site to the site list webservice. 
 */
function add_site()
{
    var site = $("#new-site").val();

    if ( !site )
    {
        return;
    }

    site = site.toLowerCase();

    $.ajax("/sites", {
        data: { "site": site },
        method: "POST"
    }).done(get_sites);
}

/**
 * Remove a site from the site list webservice.
 *
 * @param evt the remove event. The data member should contain the site name.
 */
function remove_site(evt)
{
    $.ajax("/sites/"+evt.data, {
        method: "DELETE"
    }).done(get_sites);
}

/**
 * Get a function that will toggle the current device lock/filtered state.
 */
function get_lock_device_toggle(device, is_filtered)
{
    var data = ((""+is_filtered+"").toLowerCase() == "true") ? 
        "value=False" : "value=True"

    return function(evt){
        $.ajax("/devices/"+device+"/is_filtered", {
            method: "POST",
            data: data
        }).done(get_devices);
    }
}

/**
 * Create the "new site" list item and add it to the site-list UI.  
 */
function create_new_site_li()
{
    // Create the input field
    var input = $("<input>", { id: "new-site", type: "text" });
    input.change(add_site);
    
    // Create the anchors for the input field and the icon
    var input_a = $("<a>").append(input);
    var icon_a = $("<a>")
    icon_a.click(add_site);
    
    // Add the anchors to the list item
    var li = $("<li>").append(input_a);
    li.append(icon_a);

    // Add the list item to the site list UI
    $(TRUSTED_SITES_UL).append(li);
}

/**
 * Create a list item and add it to the list UI.
 *
 * @param name the name for the list item
 */
function create_li(name, list, on_click, icon)
{
    if ( name == "" )
        return;

    var icon_attr="";
    if ( icon )
    {
        icon_attr=" data-icon=\""+icon+"\"";      
    }

    // Create the site li
    var a = $("<a>").append(name);
    var li = $("<li"+icon_attr+">").append(a);
    li.click(name, on_click);

    // Add it to the site list UI
    list.append(li);
}

/**
 * Load the site list UI with the sites list provided.
 * 
 * @param a list of sites to add to the site list UI
 */
function init_sites_list(sites)
{
    $(TRUSTED_SITES_UL).empty();

    // Create the "add site" entry
    create_new_site_li();

    // Load the site list into the listview
    sites.forEach(function(site){
        create_li(site.name, $(TRUSTED_SITES_UL), remove_site);
    });
    
    // Refresh the site listview
    $(TRUSTED_SITES_UL).listview("refresh");
}

/**
 * Load the device list UI with the devices list provided.
 * 
 * @param a list of devices to add to the site list UI
 */
function init_device_list(devices)
{
    $(KNOWN_DEVICES_UL).empty();

    // Load the device list into the listview
    devices.forEach(function(device){
        if(!device || !device.name)
            return
        
        var icon = undefined;
        if((""+device.is_filtered+"").toLowerCase() == "true")
        {
            icon="lock";
        }

        lock_device_toggle = 
            get_lock_device_toggle(device.name, device.is_filtered);
        create_li(device.display_name, $(KNOWN_DEVICES_UL), 
            lock_device_toggle, icon);
    });
  
    // Refresh the site listview
    $(KNOWN_DEVICES_UL).listview("refresh");
  
}


$(document).ready(function() {
    // Get trusted sites (and init the UI)
    get_sites();
    
    // Get known devices (and init the UI)
    get_devices();
});
