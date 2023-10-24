/**
 * Copyright 2023 Google LLC
 *
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

function exportEmailsToMarkdown(search, folderName) {
  //Checks if input folder exists or exits
  if(folderExistsOrCreate(folderName)){
    var output_file_name = folderName + "-index";
    var folderOutputObj = DriveApp.getFoldersByName(folderName);
    if (folderOutputObj.hasNext()){
      var folderOutputName = folderOutputObj.next();
    }
    var sheet = checkIndexOutputOrCreate(output_file_name, folderOutputName);
    console.log(`Searching for: "${search}"`);
    var start = 0;
    var max = 500;
    var threads = GmailApp.search(search, start, max);
    var threadMax = threads.length;
    if (threads!=null){
      console.log(threadMax + " threads found.");
    } else {
      console.warn("No threads found with the search criteria");
      return;
    }
    let timeZone = Session.getScriptTimeZone();
    let created_date = Utilities.formatDate(new Date(), timeZone, "MM-dd-yyyy HH:mm:ss z");
    sheet.appendRow(["Created: ", created_date])
    sheet.appendRow(["Date", "From", "Subject", "To", "Markdown ID", "Markdown URL", "Full date", "MD5 hash", "Status"]);
    var start_data_row = 2;
    var status = "New content";
    var newEmails = 0;
    var unchangedEmails = 0;
    for (var threadCount in threads) {
      var msgs = threads[threadCount].getMessages();
      Logger.log("Processing thread " + threadCount + " of " + threadMax);
      for (var msgCount in msgs) {
        var msg = msgs[msgCount];
        var subject = msg.getSubject().replace(/"/g, "\\\"");;
        // Removes replies and forwards - Can mostly be noise.
        if(!subject.toLowerCase().includes("re:") &&
            !subject.toLowerCase().includes("fwd:") &&
            !subject.toLowerCase().includes("forwarded message")){
          // Values to get and store messages
          var date = msg.getDate();
          let from_author = msg.getFrom().replace(/"/g, "\\\"");
          var hash_content = from_author + date + subject;
          let sanitized_subject = sanitizeString(subject);
          let date_format = Utilities.formatDate(date, "PST", "MM-dd-yyyy");
          let to = msg.getTo();
          let to_array = to.split(", ");
          for (i in to_array) {
            to_array[i] = "\"" + to_array[i].replace(/^" "/, "").replace(/"/g, "\\\"") + "\"";
          }
          let md5_hash = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5,hash_content,
                          Utilities.Charset.US_ASCII);
          let hash_str = byteToStr(md5_hash);
          //Function returns an array, assign each array value to seperate variables. For emails, only need to retrieve
          // backup markdown ids
          var backup_results = returnBackupHash(sheet, "Backup", hash_str, start_data_row, 7, 4, 5);
          if (backup_results != undefined && backup_results[0] != "no_results") {
            Logger.log("Email is already in markdown format. Skipping conversion.");
            var status = "Unchanged content";
            var markdown_id = backup_results[1];
            if (markdown_id){
              var md_file = DriveApp.getFileById(markdown_id);
            }
            unchangedEmails += 1;
          }
          else {
            var status = "New content";
            let message = msg.getPlainBody();
            let filename = sanitizeFileName(date_format + subject + ".md");
            // Initialize blank text since file will get updated with URL
            let email_md = "";
            // Add count here for emails
            newEmails += 1;
            Logger.log("Email number: " + newEmails + "| Saving email to: " + filename);
            var body = "# " + subject + "\n";
            // Cleans the reply part of emails
            body += regexToCleanCharsMD(sanitizeBody(message.replace(/^>/g,""))) + "\n";
            var destinationFolder = DriveApp.getFoldersByName(folderOutputName).next();
            // Initialize blank file to retrieve URL which is then added to the frontmatter
            var destinationFile = destinationFolder.createFile(filename, email_md , MimeType.PLAIN_TEXT);
            // Create metadata for the object
            var markdown_id = destinationFile.getId();
            var md_file = DriveApp.getFileById(markdown_id);
            let md_url = md_file.getUrl();
            let frontmatter = "---" + "\n";
            frontmatter += "title: \"" + sanitized_subject + "\"\n";
            frontmatter += "type: \"" + "email" + "\"\n";
            frontmatter += "URL: \"" + md_url + "\"\n";
            frontmatter += "created: \"" + date + "\"\n";
            frontmatter += "from: \"" + from_author + "\"\n";
            frontmatter += "to: \[" + to_array + "\]\n";
            frontmatter += "---" + "\n\n";
            email_md = frontmatter + body;
            var encoded = Utilities.base64Encode(email_md);
            var byteDataArray = Utilities.base64Decode(encoded);
            var textAsBlob = Utilities.newBlob(byteDataArray);
            Drive.Files.update(null,markdown_id, textAsBlob);
          }
          let md_chip = createRichText(md_file);
          metadata = [
            date_format,
            from_author,
            sanitized_subject,
            to,
            markdown_id,
            "md_chip",
            date,
            hash_str,
            status,
          ];
          sheet.appendRow(metadata);
          var emailTotal = newEmails + unchangedEmails;
          let row_number = emailTotal + start_data_row;
          insertRichText(sheet, md_chip, "F", row_number);
        }
      }
    }
    Logger.log("Saved a total of " + newEmails + " new emails.");
    Logger.log("There is a total of " + unchangedEmails + " unchanged emails.");
    Logger.log("Grand total of " + emailTotal + " emails.");
  }
}