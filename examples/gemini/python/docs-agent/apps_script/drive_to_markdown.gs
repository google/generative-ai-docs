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

function convertDriveFolderToMDForDocsAgent(folderName) {
  //Checks if input folder exists or exits
  if(folderExistsInput(folderName)){
    var file_count = 0;
    var folders = DriveApp.getFoldersByName(folderName);
    Logger.log("Output directory: "+ folderName + "-output");
    var folderOutput = folderName + "-output";
    var output_file_name = folderName + "-index";
    folderExistsOrCreate(folderOutput);
    var folderOutputObj = DriveApp.getFoldersByName(folderOutput);
    if (folderOutputObj.hasNext()){
      var folderOutputName = folderOutputObj.next();
    }
    var sheet = checkIndexOutputOrCreate(output_file_name, folderOutputName);
    var timeZone = Session.getScriptTimeZone();
    var date = Utilities.formatDate(new Date(), timeZone, "MM-dd-yyyy HH:mm:ss z");
    sheet.appendRow(["Created: ", date])
    sheet.appendRow(["Name","ID", "URL", "Markdown ID", "Markdown Output", "Date Created", "Last Updated", "Type", "Folder", "MD5 hash", "Status"]);
    var foldersnext = folders.next();
    var myfiles = foldersnext.getFiles();
    var new_file_count = 0;
    var unchanged_file_count = 0;
    var updated_file_count = 0;
    var gdoc_count = 0;
    var pdf_count = 0;
    var start_data_row = 2;
    var status = "New content";

    while (myfiles.hasNext()) {
      var myfile = myfiles.next();
      var ftype = myfile.getMimeType();
      // If this is a shorcut, retrieve the target file
      if (ftype == "application/vnd.google-apps.shortcut") {
        var fid = myfile.getTargetId();
        var myfile = DriveApp.getFileById(fid);
        var ftype = myfile.getMimeType();
      }
      else{
        var fid = myfile.getId();
      }
      var fname = sanitizeFileName(myfile.getName());
      var fdate = myfile.getLastUpdated();
      var furl = myfile.getUrl();
      var fcreate = myfile.getDateCreated();

      //Function returns an array, assign each array value to seperate variables
      var backup_results = returnBackupHash(sheet, "Backup", fid, start_data_row, 1, 9, 3);
      if (backup_results != undefined && backup_results[0] != "no_results") {
        var backup_fid = backup_results[0];
        var md5_backup = backup_results[1];
        var mdoutput_backup_id = backup_results[2];
      }
      if (ftype == "application/vnd.google-apps.document") {
        Logger.log("File: " + fname + " is a Google doc.");
        let gdoc = DocumentApp.openById(fid);
        let gdoc_blob = gdoc.getBody().getText();
        var md5_hash = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5,gdoc_blob,
                      Utilities.Charset.US_ASCII);
        var hash_str = byteToStr(md5_hash);
        if (backup_fid == fid && hash_str == md5_backup) {
          Logger.log("File is unchanged. Skipping conversion.");
          if (mdoutput_backup_id){
            var saved_file = DriveApp.getFileById(mdoutput_backup_id);
            var saved_file_id = saved_file.getId();
          }
          status = "Unchanged content";
          unchanged_file_count += 1;
          var convert_file = false;
        }
        else if (backup_fid == fid && hash_str != md5_backup){
          status = "Updated content";
          updated_file_count += 1;
          var convert_file = true;
        }
        else {
          status = "New content";
          new_file_count += 1;
          var convert_file = true;
        }
        if (convert_file){
          var frontmatter = "---" + "\n";
          frontmatter += "title: \"" + fname + "\"\n";
          frontmatter += "type: \"" + ftype + "\"\n";
          frontmatter += "id: \"" + fid + "\"\n";
          frontmatter += "created: \"" + fcreate + "\"\n";
          frontmatter += "updated: \"" + fdate + "\"\n";
          frontmatter += "URL: \"" + furl + "\"\n";
          frontmatter += "---" + "\n\n";
          var saved_file = convertDocumentToMarkdown(gdoc, folderOutputName, frontmatter);
          var saved_file_id = saved_file.getId();
          Logger.log("Finished converting file: " + fname + " to markdown.");
          Logger.log("Markdown file: " + saved_file);
          status = "New content";
          gdoc_count += 1;
        }
        file_count += 1;
      }
      if (ftype == "application/pdf") {
        // Converts PDFs - First to a temporary Google Doc and then use convertDocumentToMarkdown to convert to markdown with frontmatter
        Logger.log("File: " + fname + " is a PDF.");
        let pdfBlob = DriveApp.getFileById(fid).getBlob();
        let pdfblobText = pdfBlob.getDataAsString();
        var md5_hash = Utilities.computeDigest(Utilities.DigestAlgorithm.MD5,pdfblobText,
                       Utilities.Charset.US_ASCII);
        var hash_str = byteToStr(md5_hash);
        if (backup_fid == fid && hash_str == md5_backup) {
          Logger.log("File is unchanged. Skipping conversion.");
          if (mdoutput_backup_id){
            var saved_file = DriveApp.getFileById(mdoutput_backup_id);
            var saved_file_id = saved_file.getId();
          }
          status = "Unchanged content";
          unchanged_file_count += 1;
          var convert_file = false;
        }
        else if (backup_fid == fid && hash_str != md5_backup){
          status = "Updated content";
          updated_file_count += 1;
          var convert_file = true;
        }
        else {
          status = "New content";
          new_file_count += 1;
          var convert_file = true;
        }
        if (convert_file){
          let temp_doc_name = pdfBlob.getName() + "-temp";
          let temp_doc = {title: temp_doc_name, mimeType: pdfBlob.getContentType(), parents: [{id: folderOutputName.getId()}]}
          let options = {ocr: true};
          let output = Drive.Files.insert(temp_doc, pdfBlob, options);
          let output_id = output.getId();
          let gdoc = DocumentApp.openById(output_id);
          var frontmatter = "---" + "\n";
          frontmatter += "title: \"" + fname + "\"\n";
          frontmatter += "type: \"" + ftype + "\"\n";
          frontmatter += "id: \"" + fid + "\"\n";
          frontmatter += "created: \"" + fcreate + "\"\n";
          frontmatter += "updated: \"" + fdate + "\"\n";
          frontmatter += "URL: \"" + furl + "\"\n";
          frontmatter += "---" + "\n\n";
          var saved_file = convertDocumentToMarkdown(gdoc, folderOutputName, frontmatter);
          var saved_file_id = saved_file.getId();
          Logger.log("Finished converting file: "+ fname + " to markdown.");
          Logger.log("Markdown file: " + saved_file);
          Logger.log("Clearing temporary gdoc: " );
          let output_file = DriveApp.getFileById(output_id);
          output_file.setTrashed(true);
          status = "New content";
          pdf_count += 1;
        }
        file_count += 1;
      }
      let md_chip = createRichText(saved_file);
      let original_chip = createRichText(myfile);
      let folder_chip = createRichText(foldersnext);
      metadata = [
        fname,
        fid,
        "original_chip",
        saved_file_id,
        "md_chip",
        fcreate,
        fdate,
        ftype,
        "folder_chip",
        hash_str,
        status,
      ];
      row_number = file_count + start_data_row;
      sheet.appendRow(metadata);
      insertRichText(sheet, original_chip, "C", row_number);
      insertRichText(sheet, md_chip, "E", row_number);
      insertRichText(sheet, folder_chip, "I", row_number);
    }
  }
  let conversion_count = pdf_count + gdoc_count
  Logger.log("Converted a total of: " + gdoc_count + " Google Doc files.");
  Logger.log("Converted a total of: " + pdf_count + " PDF files.");
  Logger.log("Converted a grand total of: " + conversion_count + " files.");
  Logger.log("New files: " + new_file_count)
  Logger.log("Updated a total of: " + updated_file_count + " files.")
  Logger.log("Files that haven't changed: " + unchanged_file_count);
  Logger.log("Input directory had a total of: " + file_count + " files.")
}
