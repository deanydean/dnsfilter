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

/**
 * Get the all sites names from the webservice.
 */
function get_sites()
{
    $.ajax("/sites", {
        dataType: "text"       
    }).done(init_site_list);
}

/**
 */
function get_devices()
{
    $.ajax("/devices", {
        dataType: "text"
    }).done(init_device_list);
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
    }).done(get_site);
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
 * Create a site list item and add it to the site-list UI.
 *
 * @param site the site for the list item
 */
function create_site_li(site)
{
    if ( site == "" )
        return;

    // Create the site li
    var a = $("<a>").append(site);
    var li = $("<li>").append(a);
    li.click(site, remove_site);

    // Add it to the site list UI
    $(TRUSTED_SITES_UL).append(li);
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
    var sl = sites.split("\n");
    sl.forEach(create_site_li);
    
    // Refresh the site listview
    $(TRUSTED_SITES_UL).listview("refresh");
}

$(document).ready(function() {
    // Get trusted sites (and init the UI)
    get_sites();
    
    // Get known devices (and init the UI)
    get_devices();
});
