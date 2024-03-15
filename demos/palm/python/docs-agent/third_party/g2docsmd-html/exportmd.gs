/*
Parsing from mangini/gdocs2md.
Modified by clearf to add files to the google directory structure.
Modified by lmmx to write Markdown, going back to HTML-incorporation.

Usage:
  NB: don't use on top-level doc (in root Drive folder) See comment in setupScript function.
  Adding this script to your doc:
    - Tools > Script Manager > New
    - Select "Blank Project", then paste this code in and save.
  Running the script:
    - Tools > Script Manager
    - Select "convertDocumentToMarkdown" function.
    - Click Run button.
    - Converted doc will be added to a "Markdown" folder in the source document's directories.
    - Images will be added to a subfolder of the "Markdown" folder.
*/

function onInstall(e) {
  onOpen(e);
}

function onOpen() {
  // Add a menu with some items, some separators, and a sub-menu.
  setupScript();
//  In future:
//  DocumentApp.getUi().createAddonMenu();
  DocumentApp.getUi().createMenu('Markdown')
      .addItem('View as markdown', 'markdownPopup')
      .addSubMenu(DocumentApp.getUi().createMenu('Export \u2192 markdown')
                  .addItem('Export to local file', 'convertSingleDoc')
                  .addItem('Export entire folder to local file', 'convertFolder')
                  .addItem('Customise markdown conversion', 'changeDefaults'))
      .addSeparator()
      .addSubMenu(DocumentApp.getUi().createMenu('Toggle comment visibility')
                 .addItem('Image source URLs', 'toggleImageSourceStatus')
                 .addItem('All comments', 'toggleCommentStatus'))
      .addItem("Add comment", 'addCommentDummy')
      .addToUi();
}

function changeDefaults() {
  var ui = DocumentApp.getUi();
  var default_settings = '{ use your imagination... }';
  var greeting = ui.alert('This should be set up to display defaults from variables passed to getDocComments etc., e.g. something like:\n\nDefault settings are:'
                    + '\ncomments - not checking deleted comments.\nDocument - this document (alternatively specify a document ID).'
                    + '\n\nClick OK to edit these, or cancel.',
                    ui.ButtonSet.OK_CANCEL);
  ui.alert("There's not really need for this yet, so this won't proceed, regardless of what you just pressed.");
  return;

  // Future:
  if (greeting == ui.Button.CANCEL) {
    ui.alert("Alright, never mind!");
    return;
  }
  // otherwise user clicked OK
  // user clicked OK, to proceed with editing these defaults. Ask case by case whether to edit

  var response = ui.prompt('What is x (default y)?', ui.ButtonSet.YES_NO_CANCEL);

  // Example code from docs at https://developers.google.com/apps-script/reference/base/button-set
  // Process the user's response.
  if (response.getSelectedButton() == ui.Button.YES) {
    Logger.log('The user\'s name is %s.', response.getResponseText());
  } else if (response.getSelectedButton() == ui.Button.NO) {
    Logger.log('The user didn\'t want to provide a name.');
  } else {
    Logger.log('The user clicked the close button in the dialog\'s title bar.');
  }
}

function setupScript() {
  var script_properties = PropertiesService.getScriptProperties();
  script_properties.setProperty("user_email", Drive.About.get().user.emailAddress);

  // manual way to do the following:
  // script_properties.setProperty("folder_id", "INSERT_FOLDER_ID_HERE");
  // script_properties.setProperty("document_id", "INSERT_FILE_ID_HERE");

  var doc_id = DocumentApp.getActiveDocument().getId();
  script_properties.setProperty("document_id", doc_id);
  var doc_parents = DriveApp.getFileById(doc_id).getParents();
  var folders = doc_parents;
  while (folders.hasNext()) {
    var folder = folders.next();
    var folder_id = folder.getId();
  }
  script_properties.setProperty("folder_id", folder_id);
  script_properties.setProperty("image_folder_prefix", ""); // add if modifying image location
}

function addCommentDummy() {
  // Dummy function to be switched during development for addComment
  DocumentApp.getUi()
    .alert('Cancelling comment entry',
           "There's not currently a readable anchor for Google Docs - you need to write your own!"

           + "\n\nThe infrastructure for using such an anchoring schema is sketched out in"
           + " the exportmd.gs script's addComment function, for an anchor defined in anchor_props"

           + "\n\nSee github.com/lmmx/devnotes/wiki/Custom-Google-Docs-comment-anchoring-schema",
           DocumentApp.getUi().ButtonSet.OK
          );
  return;
}

function addComment() {

  var doc_id = PropertiesService.getScriptProperties().getProperty('document_id');
  var user_email = PropertiesService.getScriptProperties().getProperty('email');
/*  Drive.Comments.insert({content: "hello world",
                         context: {
                           type: 'text/html',
                           value: 'hinges'
                         }
                        }, document_id); */
  var revision_list = Drive.Revisions.list(doc_id).items;
  var recent_revision_id = revision_list[revision_list.length - 1].id;
  var anchor_props = {
    revision_id: recent_revision_id,
    starting_offset: '',
    offset_length: '',
    total_chars: ''
  }
  insertComment(doc_id, 'hinges', 'Hello world!', my_email, anchor_props);
}

function insertComment(fileId, selected_text, content, user_email, anchor_props) {

  // NB Deal with handling missing args

  /*
  anchor_props is an object with 4 properties:
    - revision_id,
    - starting_offset,
    - offset_length,
    - total_chars
  */

  var context = Drive.newCommentContext();
    context.value = selected_text;
    context.type = 'text/html';
  var comment = Drive.newComment();
    comment.kind = 'drive#comment';
    var author = Drive.newUser();
      author.kind = 'drive#user';
      author.displayName = user_email;
      author.isAuthenticatedUser = true;
    comment.author = author;
    comment.content = type;
    comment.context = context;
    comment.status = 'open';
    comment.anchor = "{'r':"
                     + anchor_props.revision_id
                     + ",'a':[{'txt':{'o':"
                     + anchor_props.starting_offset
                     + ",'l':"
                     + anchor_props.offset_length
                     + ",'ml':"
                     + anchor_props.total_chars
                     + "}}]}";
    comment.fileId = fileId;
  Drive.Comments.insert(comment, fileId);
}

function decodeScriptSwitches(optional_storage_name) {
  var property_name = (typeof(optional_storage_name) == 'string') ? optional_storage_name : 'switch_settings';
  var script_properties = PropertiesService.getScriptProperties();
  return script_properties
              .getProperty(property_name)
              .replace(/{|}/g,'')          // Get the statements out of brackets...
              .replace(',', ';');          // ...swap the separator for a semi-colon...
  // ...evaluate the stored object string as statements upon string return and voila, switches interpreted
}


function getDocComments(comment_list_settings) {
  var possible_settings = ['images', 'include_deleted'];

  // switches are processed and set on a script-wide property called "comment_switches"
  var property_name = 'comment_switches';
  switchHandler(comment_list_settings, possible_settings, property_name);

  var script_properties = PropertiesService.getScriptProperties();
  var comment_switches = decodeScriptSwitches(property_name);
  eval(comment_switches);

  var document_id = script_properties.getProperty("document_id");
  var comments_list = Drive.Comments.list(document_id,
                                          {includeDeleted: include_deleted,
                                           maxResults: 100 }); // 0 to 100, default 20
  // See https://developers.google.com/drive/v2/reference/comments/list for all options
  var comment_array = [];
  var image_sources = [];
  // To collect all comments' image URLs to match against inlineImage class elements LINK_URL attribute

  for (var i = 0; i < comments_list.items.length; i++) {
    var comment = comments_list.items[i];
    var comment_text = comment.content;
    var comment_status = comment.status;
 /*
    images is a generic parameter passed in as a switch to
    return image URL-containing comments only.

    If the parameter is provided, it's no longer undefined.
 */
    var img_url_regex = /(https?:\/\/.+?\.(png|gif|jpe?g))/;
    var has_img_url = img_url_regex.test(comment_text);

    if (images && !has_img_url) continue; // no image URL, don't store comment
    if (has_img_url) image_sources.push(RegExp.$1);
    comment_array.push(comment);
  }
  script_properties.setProperty('image_source_URLs', image_sources)
  return comment_array;
}

function isValidAttrib(attribute) { // Sanity check function, called per element in array

  // Possible list of attributes to check against (leaving out unchanging ones like kind)
  possible_attrs = [
    'selfLink',
    'commentId',
    'createdDate',
    'modifiedDate',
    'author',
    'htmlContent',
    'content',
    'deleted',
    'status',
    'context',
    'anchor',
    'fileId',
    'fileTitle',
    'replies',
    'author'
  ];

  // Check if attribute(s) provided can be used to match/filter comments:

  if (typeof(attribute) == 'string' || typeof(attribute) == 'object') {
    // Either a string/object (1-tuple)

    // Generated with Javascript, gist: https://gist.github.com/lmmx/451b301e1d78ed2c10b4

    // Return false from the function if any of the attributes specified are not in the above list

    // If an object, the name is the key, otherwise it's just the string
    if (attribute.constructor === Object) {
      var att_keys = [];
      for (var att_key in attribute) {
        if (attribute.hasOwnProperty(att_key)) {
          att_keys.push(att_key);
        }
      }
      for (var n=0; n < att_keys.length; n++) {
        var attribute_name = att_keys[n];
        var is_valid_attrib = (possible_attrs.indexOf(attribute_name) > -1);

        // The attribute needs to be one of the possible attributes listed above, match its given value(s),
        // else returning false will throw an error from onAttribError when within getCommentAttributes
        return is_valid_attrib;
      }
    } else if (typeof(attribute) == 'string') {
      var attribute_name = attribute;
      var is_valid_attrib = (possible_attrs.indexOf(attribute_name) > -1);
      return is_valid_attrib;
      // Otherwise is a valid (string) attribute
    } else if (attribute.constructor === Array) {
      return false; // Again, if within getCommentAttributes this will cause an error - shouldn't pass an array
    } else {
      // Wouldn't expect this to happen, so give a custom error message
      Logger.log('Unknown type (assumed impossible) passed to isValidAttrib: ', attribute, attribute.constructor);
      throw new TypeError('Unknown passed to isValidAttrib - this should be receiving 1-tuples only, see logs for details.');
    }
  } else return false; // Neither string/object / array of strings &/or objects - not a valid attribute
}

function getCommentAttributes(attributes, comment_list_settings) {

  // A filter function built on Comments.list, for a given list of attributes
  // Objects' values are ignored here, only their property titles are used to filter comments.


  /*
    - attributes: array of attributes to filter/match on
    - comment_list_settings: (optional) object with properties corresponding to switches in getDocComments

    This function outputs an array of the same length as the comment list, containing
    values for all fields matched/filtered on.
  */


  /*
   *         All possible comment attributes are listed at:
   *   https://developers.google.com/drive/v2/reference/comments#properties
   */

  //  Firstly, describe the type in a message to be thrown in case of TypeError:

  var attrib_def_message = "'attributes' should be a string (the attribute to get for each comment), "
                           + "an object (a key-value pair for attribute and desired value), "
                           + "or an array of objects (each with key-value pairs)";

  function onAttribError(message) {
    Logger.log(message);
    throw new TypeError(message);
  }

  // If (optional) comment_list_settings isn't set, make a getDocComments call with switches left blank.
  if (typeof(comment_list_settings) == 'undefined') var comment_list_settings = {};
  if (typeof(attributes) == 'undefined') onAttribError(attrib_def_message); // no variables specified

  if (isValidAttrib(attributes)) { // This will be true if there's only one attribute, not provided in an array

    /*
       Make a 1-tuple (array of 1) from either an object or a string,
       i.e. a single attribute, with or without a defined value respectively.
    */

    var attributes = Array(attributes);

  } else if (attributes.constructor === Array) {

    // Check each item in the array is a valid attribute specification
    for (var l = 0; l < attributes.length; l++) {
      if (! isValidAttrib(attributes[l]) ) {
        onAttribError('Error in attribute '
                      + (l+1) + ' of ' + attributes.length
                      + '\n\n' + + attrib_def_message);
      }
    }

  } else { // Neither attribute nor array of attributes
    throw new TypeError(attrib_def_message);
  }

  // Attributes now holds an array of string and/or objects specifying a comment match and/or filter query

  var comment_list = getDocComments(comment_list_settings);
  var comment_attrib_lists = [];
  for (var i in comment_list) {
    var comment = comment_list[i];
    var comment_attrib_list = [];
    for (var j in attributes) {
      var comment_attribute = comment_list[i][attributes[j]];
      comment_attrib_list.push(comment_attribute);
    }
    comment_attrib_lists.push(comment_attrib_list);
  }
  // The array comment_attrib_lists is now full of the requested attributes,
  // of length equal to that of attributes
  return comment_attrib_lists;
}

// Example function to use getCommentAttributes:

function filterComments(attributes, comment_list_settings) {
  var comment_attributes = getCommentAttributes(attributes, comment_list_settings);
  var m = attribs.indexOf('commentId') // no need to keep track of commentID array position
  comm_attribs.map(function(attrib_pair) {
     if (attrib_pair[1]);
  })
}

function toggleCommentStatus(comment_switches){
  // Technically just image URL-containing comments, not sources just yet
  var attribs = ['commentId', 'status'];
  var comm_attribs = getCommentAttributes(attribs, comment_switches);
  var rearrangement = [];
  comm_attribs.map(
    function(attrib_pair) { // for every comment return with the images_only / images: true comments.list setting,
      switch (attrib_pair[1]){ // check the status of each
        case 'open':
          rearrangement.push([attrib_pair[0],'resolved']);
          break;
        case 'resolved':
          rearrangement.push([attrib_pair[0],'open']);
          break;
      }
    }
  );
  var script_properties = PropertiesService.getScriptProperties();
  var doc_id = script_properties.getProperty("document_id");
  rearrangement.map(
    function(new_attrib_pair) { // for every comment ID with flipped status
      Drive.Comments.patch('{"status": "'
                           + new_attrib_pair[1]
                           + '"}', doc_id, new_attrib_pair[0])
    }
  );
  return;
}

function toggleImageSourceStatus(){
  toggleCommentStatus({images: true});
}

function flipResolved() {
  // Flip the status of resolved comments to open, and open comments to resolved (respectful = true)
  // I.e. make resolved URL-containing comments visible, without losing track of normal comments' status

  // To force all comments' statuses to switch between resolved and open en masse set respectful to false

  var switch_settings = {};
    switch_settings.respectful = true;
    switch_settings.images_only = false; // If true, only switch status of comments with an image URL
    switch_settings.switch_deleted_comments = false; // If true, also switch status of deleted comments

  var comments_list = getDocComments(
    { images: switch_settings.images_only,
      include_deleted: switch_settings.switch_deleted_comments });

  // Note: these parameters are unnecessary if both false (in their absence assumed false)
  //       but included for ease of later reuse

  if (switch_settings.respectful) {
    // flip between
  } else {
    // flip all based on status of first in list
  }
}

function markdownPopup() {
  var css_style = '<style type="text/css" data-github="https://github.com/lmmx/gdocs2md-html/blob/master/md-preview.css">'
    + 'h1, h2, h3, h4, h5, h6 {'
    + '  font-family: "Gibson", sans-serif, "Helvetica Neue", HelveticaNeue, Helvetica, Arial, sans-serif;'
    + '  font-size: 1.3em;'
    + '  line-height: 1.4;'
    + '  margin-top: 9px;'
    + '}'
    + 'code,pre,pre *{'
    + '  font-size: 12px;'
    + '  line-height: 1.4;'
    + '  white-space: pre-wrap;'
    + '  padding-top: 1em;'
    + '  padding-bottom: 1em;'
    + '  clear:both;'
    + '  padding: 0.2em;'
    + '  margin: 0;'
    + '  background-color: rgba(0,0,0,0.04);'
    + '  border-radius: 3px;'
    + '  font: 11px Consolas, "Liberation Mono", Menlo, Courier, monospace;'
    + '}'
    + 'pre textarea {'
    + '    background: transparent;'
    + '    border: none;'
    + '    height: inherit !important;'
    + '    width: 775px;'
    + '}'
    + 'pre {'
    + '    height: 430px;'
    + '}'
    + '</style>';

  // The above was written with js since <link rel="stylesheet" href=[GitHub raw URL]> doesn't work:
  // https://gist.github.com/lmmx/ec084fc351528395f2bb

  var mdstring = stringMiddleMan();

  var htmlstring =
      '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    + css_style
    + '</head><body><pre><textarea id="md-output" readonly="readonly">'
    + mdstring
    + '</textarea></pre><script type="text/javascript">'
    + 'function mdClick() {'
    + 'var textbox = document.getElementById("md-output");'
    + 'textbox.setAttribute("onclick", "this.focus(); this.select();") }'
    + 'window.onload = mdClick();'
    + '</script></body></html>';

  var html5 = HtmlService.createHtmlOutput(htmlstring)
      .setSandboxMode(HtmlService.SandboxMode.IFRAME)
      .setWidth(800)
      .setHeight(500);

  DocumentApp.getUi()
      .showModalDialog(html5, 'Markdown output');
}

function stringMiddleMan() {
  var returned_string;
  convertSingleDoc({"return_string": true}); // for some reason needs the scope to be already set...
  // could probably rework to use mdstring rather than returned_string, cut out middle man function
  return this.returned_string;
}

function convertSingleDoc(optional_switches) {
  var script_properties = PropertiesService.getScriptProperties();
  // renew comments list on every export
  var doc_comments = getDocComments();
  var image_urls = getDocComments({images: true}); // NB assumed false - any value will do
  script_properties.setProperty("comments", doc_comments);
  script_properties.setProperty("image_srcs", image_urls);
  var folder_id = script_properties.getProperty("folder_id");
  var document_id = script_properties.getProperty("document_id");
  var source_folder = DriveApp.getFolderById(folder_id);
  var markdown_folders = source_folder.getFoldersByName("Markdown");

  var markdown_folder;
  if (markdown_folders.hasNext()) {
    markdown_folder = markdown_folders.next();
  } else {
    // Create a Markdown folder if it doesn't exist.
    markdown_folder = source_folder.createFolder("Markdown")
  }

  convertDocumentToMarkdown(DocumentApp.openById(document_id), markdown_folder, optional_switches);
}

function convertFolder() {
  var script_properties = PropertiesService.getScriptProperties();
  var folder_id = script_properties.getProperty("folder_id");
  var source_folder = DriveApp.getFolderById(folder_id);
  var markdown_folders = source_folder.getFoldersByName("Markdown");


  var markdown_folder;
  if (markdown_folders.hasNext()) {
    markdown_folder = markdown_folders.next();
  } else {
    // Create a Markdown folder if it doesn't exist.
    markdown_folder = source_folder.createFolder("Markdown");
  }

  // Only try to convert google docs files.
  var gdoc_files = source_folder.getFilesByType("application/vnd.google-apps.document");

  // For every file in this directory
  while(gdoc_files.hasNext()) {
    var gdoc_file = gdoc_files.next()

    var filename = gdoc_file.getName();
    var md_files = markdown_folder.getFilesByName(filename + ".md");
    var update_file = false;

    if (md_files.hasNext()) {
      var md_file = md_files.next();

      if (md_files.hasNext()){ // There are multiple markdown files; delete and rerun
        update_file = true;
      } else if (md_file.getLastUpdated() < gdoc_file.getLastUpdated()) {
        update_file = true;
      }
    } else {
      // There is no folder and the conversion needs to be rerun
      update_file = true;
    }

    if (update_file) {
      convertDocumentToMarkdown(DocumentApp.openById(gdoc_file.getId()), markdown_folder);
    }
  }
}

function switchHandler(input_switches, potential_switches, optional_storage_name) {

  // Firstly, if no input switches were set, make an empty input object
  if (typeof(input_switches) == 'undefined') input_switches = {};

  // Use optional storage name if it's defined (must be a string), else use default variable name "switch_settings"
  var property_name = (typeof(optional_storage_name) == 'string') ? optional_storage_name : 'switch_settings';

  // Make a blank object to be populated and stored as the script-wide property named after property_name
  var switch_settings = {};

  for (var i in potential_switches) {
    var potential_switch = potential_switches[i];

    // If each switch has been set (in input_switches), evaluate it, else assume it's switched off (false):

    if (input_switches.propertyIsEnumerable(potential_switch)) {

      // Evaluates a string representing a statement which sets switch_settings properties from input_switches
      // e.g. "switch_settings.images = true" when input_switches = {images: true}

      eval('switch_settings.' + potential_switch + " = " + input_switches[potential_switch]);

    } else {

      // Alternatively, the evaluated statement sets anything absent from the input_switches object as false
      // e.g. "switch_settings.images = false" when input_switches = {} and potential_switches = ['images']

      eval('switch_settings.' + potential_switch + " = false");
    }
  }

  PropertiesService.getScriptProperties().setProperty(property_name, switch_settings);

  /*
  Looks bad but more sensible than repeatedly checking if arg undefined.

  Sets every variable named in the potential_switches array to false if
  it wasn't passed into the input_switches object, otherwise evaluates.

  Any arguments not passed in are false, but so are any explicitly passed in as false:
  all parameters are therefore Boolean until otherwise specified.
  */

}

function convertDocumentToMarkdown(document, destination_folder, optional_switches) {
  // if returning a string, force_save_images will make the script continue - experimental
  var possible_switches = ['return_string', 'force_save_images'];
  var property_name = 'conversion_switches';
  switchHandler(optional_switches, possible_switches, property_name);

  // TODO switch off image storage if force_save_images is true - not necessary for normal behaviour
  var script_properties = PropertiesService.getScriptProperties();
  var comment_switches = decodeScriptSwitches(property_name);
  eval(comment_switches);

  var image_prefix = script_properties.getProperty("image_folder_prefix");
  var numChildren = document.getActiveSection().getNumChildren();
  var text = "";
  var md_filename = document.getName()+".md";
  var image_foldername = document.getName()+"_images";
  var inSrc = false;
  var inClass = false;
  var globalImageCounter = 0;
  var globalListCounters = {};
  // edbacher: added a variable for indent in src <pre> block. Let style sheet do margin.
  var srcIndent = "";

  var postHasImages = false;

  var files = [];

  // Walk through all the child elements of the doc.
  for (var i = 0; i < numChildren; i++) {
    var child = document.getActiveSection().getChild(i);
    var result = processParagraph(i, child, inSrc, globalImageCounter, globalListCounters, image_prefix + image_foldername);
    globalImageCounter += (result && result.images) ? result.images.length : 0;
    if (result!==null) {
      if (result.sourceGlossary==="start" && !inSrc) {
        inSrc=true;
        text+="<pre class=\"glossary\">\n";
      } else if (result.sourceGlossary==="end" && inSrc) {
        inSrc=false;
        text+="</pre>\n\n";
      } else if (result.sourceFigCap==="start" && !inSrc) {
        inSrc=true;
        text+="<pre class=\"glossary\">\n";
      } else if (result.sourceFigCap==="end" && inSrc) {
        inSrc=false;
        text+="</pre>\n\n";
      } else if (result.source==="start" && !inSrc) {
        inSrc=true;
        text+="<pre>\n";
      } else if (result.source==="end" && inSrc) {
        inSrc=false;
        text+="</pre>\n\n";
      } else if (result.inClass==="start" && !inClass) {
        inClass=true;
        text+="<pre class=\""+result.className+"\">\n";
      } else if (result.inClass==="end" && inClass) {
        inClass=false;
        text+="</pre>\n\n";
      } else if (inClass) {
        text+=result.text+"\n\n";
      } else if (inSrc) {
        text+=(srcIndent+escapeHTML(result.text)+"\n");
      } else if (result.text && result.text.length>0) {
        text+=result.text+"\n\n";
      }

      if (result.images && result.images.length>0) {
        for (var j=0; j<result.images.length; j++) {
          files.push( { "blob": result.images[j].blob } );
          postHasImages = true;
        }
      }
    } else if (inSrc) { // support empty lines inside source code
      text+='\n';
    }

  }

  if (return_string && !force_save_images) {
    returned_string = text;
    return returned_string;
  }
  // return the string rather than continuing to write files

  // I don't need to handle string return *with* saved images yet so this flag doesn't do anything in absence of return_string

  files.push({"fileName": md_filename, "mimeType": "text/plain", "content": text});


  // Cleanup any old folders and files in our destination directory with an identical name
  var old_folders = destination_folder.getFoldersByName(image_foldername)
  while (old_folders.hasNext()) {
    var old_folder = old_folders.next();
    old_folder.setTrashed(true)
  }

  // Remove any previously converted markdown files.
  var old_files = destination_folder.getFilesByName(md_filename)
  while (old_files.hasNext()) {
    var old_file = old_files.next();
    old_file.setTrashed(true)
  }

  // Create a subfolder for images if they exist
  var image_folder;
  if (postHasImages) {
    image_folder = DriveApp.createFolder(image_foldername);
    DriveApp.removeFolder(image_folder); // Confusing convention; this just removes the folder from the google drive root.
    destination_folder.addFolder(image_folder)
  }

  for (var i = 0; i < files.length; i++) {
    var saved_file;
    if (files[i].blob) {
      saved_file = DriveApp.createFile(files[i].blob)
      // The images go into a subfolder matching the post title
      image_folder.addFile(saved_file)
    } else {
      // The markdown files all go in the "Markdown" directory
      saved_file = DriveApp.createFile(files[i]["fileName"], files[i]["content"], files[i]["mimeType"])
      destination_folder.addFile(saved_file)
    }
   DriveApp.removeFile(saved_file) // Removes from google drive root.
  }

}

function escapeHTML(text) {
  return text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function standardQMarks(text) {
  return text.replace(/\u2018|\u8216|\u2019|\u8217/g,"'").replace(/\u201c|\u8220|\u201d|\u8221/g, '"')
}

// Process each child element (not just paragraphs).
function processParagraph(index, element, inSrc, imageCounter, listCounters, image_path) {
  // First, check for things that require no processing.
  if (element.getNumChildren()==0) {
    return null;
  }
  // Skip on TOC.
  if (element.getType() === DocumentApp.ElementType.TABLE_OF_CONTENTS) {
    return {"text": "[[TOC]]"};
  }

  // Set up for real results.
  var result = {};
  var pOut = "";
  var textElements = [];
  var imagePrefix = "image_";

  // Handle Table elements. Pretty simple-minded now, but works for simple tables.
  // Note that Markdown does not process within block-level HTML, so it probably
  // doesn't make sense to add markup within tables.
  if (element.getType() === DocumentApp.ElementType.TABLE) {
    textElements.push("<table>\n");
    var nCols = element.getChild(0).getNumCells();
    for (var i = 0; i < element.getNumChildren(); i++) {
      textElements.push("  <tr>\n");
      // process this row
      for (var j = 0; j < nCols; j++) {
        textElements.push("    <td>" + element.getChild(i).getChild(j).getText() + "</td>\n");
      }
      textElements.push("  </tr>\n");
    }
    textElements.push("</table>\n");
  }

  // Process various types (ElementType).
  for (var i = 0; i < element.getNumChildren(); i++) {
    var t = element.getChild(i).getType();

    if (t === DocumentApp.ElementType.TABLE_ROW) {
      // do nothing: already handled TABLE_ROW
    } else if (t === DocumentApp.ElementType.TEXT) {
      var txt  = element.getChild(i);
      pOut += txt.getText();
      textElements.push(txt);
    } else if (t === DocumentApp.ElementType.INLINE_IMAGE) {
      var imglink = element.getChild(i).getLinkUrl();
      result.images = result.images || [];
      var blob = element.getChild(i).getBlob()
      var contentType = blob.getContentType();
      var extension = "";
      if (/\/png$/.test(contentType)) {
        extension = ".png";
      } else if (/\/gif$/.test(contentType)) {
        extension = ".gif";
      } else if (/\/jpe?g$/.test(contentType)) {
        extension = ".jpg";
      } else {
        throw "Unsupported image type: "+contentType;
      }

      var name = imagePrefix + imageCounter + extension;
      blob.setName(name);

      imageCounter++;
      if (!return_string || force_save_images) {
        textElements.push('![](' + image_path + '/' + name + ')');
      } else {
        textElements.push('![](' + imglink + ')');
      }
      //result.images.push( {
      //  "bytes": blob.getBytes(),
      //  "type": contentType,
      //  "name": name});

      result.images.push({ "blob" : blob } )

    } else if (t === DocumentApp.ElementType.PAGE_BREAK) {
      // ignore
    } else if (t === DocumentApp.ElementType.HORIZONTAL_RULE) {
      textElements.push('* * *\n');
    } else if (t === DocumentApp.ElementType.FOOTNOTE) {
      textElements.push(' ('+element.getChild(i).getFootnoteContents().getText()+')');
    } else {
      throw "Paragraph "+index+" of type "+element.getType()+" has an unsupported child: "
      +t+" "+(element.getChild(i)["getText"] ? element.getChild(i).getText():'')+" index="+index;
    }
  }

  if (textElements.length==0) {
    // Isn't result empty now?
    return result;
  }

  var ind_f = element.getIndentFirstLine();
  var ind_s = element.getIndentStart();
  var ind_e = element.getIndentEnd();
  var i_fse = ['ind_f','ind_s','ind_e'];
  var indents = {};
  for (indt=0;indt<i_fse.length;indt++) {
    var indname = i_fse[indt];
    if (eval(indname) > 0) indents[indname] = eval(indname);
    // lazy test, null (no indent) is not greater than zero, but becomes set if indent 'undone'
  }
  var inIndent = (Object.keys(indents).length > 0);

  // evb: Add glossary and figure caption too. (And abbreviations: gloss and fig-cap.)
  // process source code block:
  if (/^\s*---\s+gloss\s*$/.test(pOut) || /^\s*---\s+source glossary\s*$/.test(pOut)) {
    result.sourceGlossary = "start";
  } else if (/^\s*---\s+fig-cap\s*$/.test(pOut) || /^\s*---\s+source fig-cap\s*$/.test(pOut)) {
    result.sourceFigCap = "start";
  } else if (/^\s*---\s+src\s*$/.test(pOut) || /^\s*---\s+source code\s*$/.test(pOut)) {
    result.source = "start";
  } else if (/^\s*---\s+class\s+([^ ]+)\s*$/.test(pOut)) {
    result.inClass = "start";
    result.className = RegExp.$1.replace(/\./g,' ');
  } else if (/^\s*---\s*$/.test(pOut)) {
    result.source = "end";
    result.sourceGlossary = "end";
    result.sourceFigCap = "end";
    result.inClass = "end";
  } else if (/^\s*---\s+jsperf\s*([^ ]+)\s*$/.test(pOut)) {
    result.text = '<iframe style="width: 100%; height: 240px; overflow: hidden; border: 0;" '+
                  'src="http://www.html5rocks.com/static/jsperfview/embed.html?id='+RegExp.$1+
                  '"></iframe>';
  } else {

    prefix = findPrefix(inSrc, element, listCounters);

    var pOut = "";
    for (var i=0; i<textElements.length; i++) {
      pOut += processTextElement(inSrc, textElements[i]);
    }

    // replace Unicode quotation marks (double and single)
    pOut = standardQMarks(pOut);

    result.text = prefix+pOut;
  }

  var indent_prefix = '> ';
# var indent_alt_prefix = '> <sub>';
  if (inIndent && !inSrc) {
    if (/^#*\s/.test(result.text)) { // don't subscript-prefix header prefix
      result.text = indent_alt_prefix + result.text;
    } else {
      result.text = indent_prefix + result.text;
    }
  }

  return result;
}

// Add correct prefix to list items.
function findPrefix(inSrc, element, listCounters) {
  var prefix = "";
  if (!inSrc) {
    if (element.getType()===DocumentApp.ElementType.PARAGRAPH) {
      var paragraphObj = element;
      switch (paragraphObj.getHeading()) {
        // Add a # for each heading level. No break, so we accumulate the right number.
        case DocumentApp.ParagraphHeading.HEADING6: prefix+="#";
        case DocumentApp.ParagraphHeading.HEADING5: prefix+="#";
        case DocumentApp.ParagraphHeading.HEADING4: prefix+="#";
        case DocumentApp.ParagraphHeading.HEADING3: prefix+="#";
        case DocumentApp.ParagraphHeading.HEADING2: prefix+="#";
        case DocumentApp.ParagraphHeading.HEADING1: prefix+="# ";
        default:
      }
    } else if (element.getType()===DocumentApp.ElementType.LIST_ITEM) {
      var listItem = element;
      var nesting = listItem.getNestingLevel()
      for (var i=0; i<nesting; i++) {
        prefix += "    ";
      }
      var gt = listItem.getGlyphType();
      // Bullet list (<ul>):
      if (gt === DocumentApp.GlyphType.BULLET
          || gt === DocumentApp.GlyphType.HOLLOW_BULLET
          || gt === DocumentApp.GlyphType.SQUARE_BULLET) {
        prefix += "* ";
      } else {
        // Ordered list (<ol>):
        var key = listItem.getListId() + '.' + listItem.getNestingLevel();
        var counter = listCounters[key] || 0;
        counter++;
        listCounters[key] = counter;
        prefix += counter+". ";
      }
    }
  }
  return prefix;
}

function processTextElement(inSrc, txt) {
  if (typeof(txt) === 'string') {
    return txt;
  }

  var pOut = txt.getText();
  if (! txt.getTextAttributeIndices) {
    return pOut;
  }

//  Logger.log("Initial String: " + pOut)

  // CRC introducing reformatted_txt to let us apply rational formatting that we can actually parse
  var reformatted_txt = txt.copy();
  reformatted_txt.deleteText(0,pOut.length-1);
  reformatted_txt = reformatted_txt.setText(pOut);

  var attrs = txt.getTextAttributeIndices();
  var lastOff = pOut.length;
  // We will run through this loop multiple times for the things we care about.
  // Font
  // URL
  // Then for alignment
  // Then for bold
  // Then for italic.

  // FONTs
  var lastOff = pOut.length; // loop goes backwards, so this holds
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var font=txt.getFontFamily(off)
     if (font) {
       while (i>=1 && txt.getFontFamily(attrs[i-1])==font) {
          // detect fonts that are in multiple pieces because of errors on formatting:
          i-=1;
          off=attrs[i];
       }
       reformatted_txt.setFontFamily(off, lastOff-1, font);
     }
    lastOff=off;
  }

  // URL
  // XXX TODO actually convert to URL text here.
  var lastOff=pOut.length;
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var url=txt.getLinkUrl(off);
     if (url) {
       while (i>=1 && txt.getLinkUrl(attrs[i-1]) == url) {
          // detect urls that are in multiple pieces because of errors on formatting:
          i-=1;
          off=attrs[i];
       }
     reformatted_txt.setLinkUrl(off, lastOff-1, url);
     }
    lastOff=off;
  }

  // alignment
  var lastOff=pOut.length;
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var alignment=txt.getTextAlignment(off);
     if (alignment) { //
       while (i>=1 && txt.getTextAlignment(attrs[i-1]) == alignment) {
          i-=1;
          off=attrs[i];
       }
     reformatted_txt.setTextAlignment(off, lastOff-1, alignment);
     }
    lastOff=off;
  }

  // strike
  var lastOff=pOut.length;
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var strike=txt.isStrikethrough(off);
     if (strike) {
       while (i>=1 && txt.isStrikethrough(attrs[i-1])) {
          i-=1;
          off=attrs[i];
       }
     reformatted_txt.setStrikethrough(off, lastOff-1, strike);
     }
    lastOff=off;
  }

  // bold
  var lastOff=pOut.length;
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var bold=txt.isBold(off);
     if (bold) {
       while (i>=1 && txt.isBold(attrs[i-1])) {
          i-=1;
          off=attrs[i];
       }
     reformatted_txt.setBold(off, lastOff-1, bold);
     }
    lastOff=off;
  }

  // italics
  var lastOff=pOut.length;
  for (var i=attrs.length-1; i>=0; i--) {
    var off=attrs[i];
    var italic=txt.isItalic(off);
     if (italic) {
       while (i>=1 && txt.isItalic(attrs[i-1])) {
          i-=1;
          off=attrs[i];
       }
     reformatted_txt.setItalic(off, lastOff-1, italic);
     }
    lastOff=off;
  }


  var mOut=""; // Modified out string
  var harmonized_attrs = reformatted_txt.getTextAttributeIndices();
  reformatted_txt.getTextAttributeIndices(); // @lmmx: is this a typo...?
  pOut = reformatted_txt.getText();


  // Markdown is farily picky about how it will let you intersperse spaces around words and strong/italics chars. This regex (hopefully) clears this up
  // Match any number of \*, followed by spaces/word boundaries against anything that is not the \*, followed by boundaries, spaces and * again.
  // Test case at http://jsfiddle.net/ovqLv0s9/2/

  var reAlignStars = /(\*+)(\s*\b)([^\*]+)(\b\s*)(\*+)/g;

  var lastOff=pOut.length;
  for (var i=harmonized_attrs.length-1; i>=0; i--) {
    var off=harmonized_attrs[i];

    var raw_text = pOut.substring(off, lastOff)

    var d1 = ""; // @lmmx: build up a modifier prefix
    var d2 = ""; // @lmmx: ...and suffix

    var end_font;

    var mark_bold = false;
    var mark_italic = false;
    var mark_code = false;
    var mark_sup = false;
    var mark_sub = false;
    var mark_strike = false;

    // The end of the text block is a special case.
    if (lastOff == pOut.length) {
      end_font = reformatted_txt.getFontFamily(lastOff - 1)
      if (end_font) {
        if (!inSrc && end_font===end_font.COURIER_NEW) {
          mark_code = true;
        }
      }
      if (reformatted_txt.isBold(lastOff -1)) {
        mark_bold = true;
      }
      if (reformatted_txt.isItalic(lastOff - 1)) {
        // edbacher: changed this to handle bold italic properly.
        mark_italic = true;
      }
      if (reformatted_txt.isStrikethrough(lastOff - 1)) {
        mark_strike = true;
      }
      if (reformatted_txt.getTextAlignment(lastOff - 1)===DocumentApp.TextAlignment.SUPERSCRIPT) {
        mark_sup = true;
      }
      if (reformatted_txt.getTextAlignment(lastOff - 1)===DocumentApp.TextAlignment.SUBSCRIPT) {
        mark_sub = true;
      }
    } else {
      end_font = reformatted_txt.getFontFamily(lastOff -1 )
      if (end_font) {
        if (!inSrc && end_font===end_font.COURIER_NEW && reformatted_txt.getFontFamily(lastOff) != end_font) {
          mark_code=true;
        }
      }
      if (reformatted_txt.isBold(lastOff - 1) && !reformatted_txt.isBold(lastOff) ) {
        mark_bold=true;
      }
      if (reformatted_txt.isStrikethrough(lastOff - 1) && !reformatted_txt.isStrikethrough(lastOff)) {
        mark_strike=true;
      }
      if (reformatted_txt.isItalic(lastOff - 1) && !reformatted_txt.isItalic(lastOff)) {
        mark_italic=true;
      }
      if (reformatted_txt.getTextAlignment(lastOff - 1)===DocumentApp.TextAlignment.SUPERSCRIPT) {
        if (reformatted_txt.getTextAlignment(lastOff)!==DocumentApp.TextAlignment.SUPERSCRIPT) {
          mark_sup = true;
        }
      }
      if (reformatted_txt.getTextAlignment(lastOff - 1)===DocumentApp.TextAlignment.SUBSCRIPT) {
        if (reformatted_txt.getTextAlignment(lastOff)!==DocumentApp.TextAlignment.SUBSCRIPT) {
          mark_sub = true;
        }
      }
    }

    if (mark_code) {
      d2 = '`'; // shouldn't these go last? or will it interfere w/ reAlignStars?
    }
    if (mark_bold) {
      d2 = "**" + d2;
    }
    if (mark_italic) {
      d2 = "*" + d2;
    }
    if (mark_strike) {
      d2 = "</strike>" + d2;
    }
    if (mark_sup) {
      d2 = '</sup>' + d2;
    }
    if (mark_sub) {
      d2 = '</sub>' + d2;
    }

    mark_bold = mark_italic = mark_code = mark_sup = mark_sub = mark_strike = false;

    var font=reformatted_txt.getFontFamily(off);
    if (off == 0) {
      if (font) {
        if (!inSrc && font===font.COURIER_NEW) {
          mark_code = true;
        }
      }
      if (reformatted_txt.isBold(off)) {
        mark_bold = true;
      }
      if (reformatted_txt.isItalic(off)) {
        mark_italic = true;
      }
      if (reformatted_txt.isStrikethrough(off)) {
        mark_strike = true;
      }
      if (reformatted_txt.getTextAlignment(off)===DocumentApp.TextAlignment.SUPERSCRIPT) {
        mark_sup = true;
      }
      if (reformatted_txt.getTextAlignment(off)===DocumentApp.TextAlignment.SUBSCRIPT) {
        mark_sub = true;
      }
    } else {
      if (font) {
        if (!inSrc && font===font.COURIER_NEW && reformatted_txt.getFontFamily(off - 1) != font) {
          mark_code=true;
        }
      }
      if (reformatted_txt.isBold(off) && !reformatted_txt.isBold(off -1) ) {
        mark_bold=true;
      }
      if (reformatted_txt.isItalic(off) && !reformatted_txt.isItalic(off - 1)) {
        mark_italic=true;
      }
      if (reformatted_txt.isStrikethrough(off) && !reformatted_txt.isStrikethrough(off - 1)) {
        mark_strike=true;
      }
      if (reformatted_txt.getTextAlignment(off)===DocumentApp.TextAlignment.SUPERSCRIPT) {
        if (reformatted_txt.getTextAlignment(off - 1)!==DocumentApp.TextAlignment.SUPERSCRIPT) {
          mark_sup = true;
        }
      }
      if (reformatted_txt.getTextAlignment(off)===DocumentApp.TextAlignment.SUBSCRIPT) {
        if (reformatted_txt.getTextAlignment(off - 1)!==DocumentApp.TextAlignment.SUBSCRIPT) {
          mark_sub = true;
        }
      }
    }


    if (mark_code) {
      d1 = '`';
    }

    if (mark_bold) {
      d1 = d1 + "**";
    }

    if (mark_italic) {
      d1 = d1 + "*";
    }

    if (mark_sup) {
      d1 = d1 + '<sup>';
    }

    if (mark_sub) {
      d1 = d1 + '<sub>';
    }

    if (mark_strike) {
      d1 = d1 + '<strike>';
    }

    var url=reformatted_txt.getLinkUrl(off);
    if (url) {
      mOut = d1 + '['+ raw_text +']('+url+')' + d2 + mOut;
    } else {
      var new_text = d1 + raw_text + d2;
      new_text = new_text.replace(reAlignStars, "$2$1$3$5$4");
      mOut =  new_text + mOut;
    }

    lastOff=off;
//    Logger.log("Modified String: " + mOut)
  }

  mOut = pOut.substring(0, off) + mOut;
  return mOut;
}