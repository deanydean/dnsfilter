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

/**
 * Get the all domains names from the webservice.
 */
function get_domains()
{
    $.ajax("/domains", {
        dataType: "text"       
    }).done(init_domain_list);
}

/**
 * Add a domain to the domain list webservice. 
 */
function add_domain()
{
    var domain = $("#new-domain").val();

    if ( !domain )
    {
        return;
    }

    domain = domain.toLowerCase();

    $.ajax("/domains", {
        data: { "domain": domain },
        method: "POST"
    }).done(get_domains);
}

/**
 * Remove a domain from the domain list webservice.
 *
 * @param evt the remove event. The data member should contain the domain name.
 */
function remove_domain(evt)
{
    $.ajax("/domains/"+evt.data, {
        method: "DELETE"
    }).done(get_domains);
}

/**
 * Create the "new domain" list item and add it to the domain-list UI.  
 */
function create_new_domain_li()
{
    // Create the input field
    var input = $("<input>", { id: "new-domain", type: "text" });
    input.change(add_domain);
    
    // Create the anchors for the input field and the icon
    var input_a = $("<a>").append(input);
    var icon_a = $("<a>")
    icon_a.click(add_domain);
    
    // Add the anchors to the list item
    var li = $("<li>").append(input_a);
    li.append(icon_a);

    // Add the list item to the domain list UI
    $("#domain-list").append(li);
}

/**
 * Create a domain list item and add it to the domain-list UI.
 *
 * @param domain the domain for the list item
 */
function create_domain_li(domain)
{
    if ( domain == "" )
        return;

    // Create the domain li
    var a = $("<a>").append(domain);
    var li = $("<li>").append(a);
    li.click(domain, remove_domain);

    // Add it to the domain list UI
    $("#domain-list").append(li);
}

/**
 * Load the domain list UI with the domains list provided.
 * 
 * @param a list of domains to add to the domain list UI
 */
function init_domain_list(domains)
{
    $("#domain-list").empty();

    // Create the "add domain" entry
    create_new_domain_li();

    // Load the domain list into the listview
    var dl = domains.split("\n");
    dl.forEach(create_domain_li);
    
    // Refresh the domain listview
    $("#domain-list").listview("refresh");
}

$(document).ready(function() {
    // Get domains (and init the domains list UI)
    get_domains();
});
