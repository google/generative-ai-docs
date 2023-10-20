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

// Checks to see if a folder already exists in the drive
function folderExists(folderName) {
  const folderIterator = DriveApp.getRootFolder().getFoldersByName(folderName);
  if(folderIterator.hasNext()) {
    return true;
  }
  else {
    return false;
  }
}

// Checks to see if a folder already exists in the drive and exits if it doesn't. Useful for input directories
function folderExistsInput(folderName){
  if (folderExists(folderName)) {
    Logger.log("Folder exists: "+ folderName);
    return true;
  }
  else {
    Logger.log("Folder does not exist: "+ folderName + ". Please make sure the directory exists.");
    return false;
  }
}

// Checks to see if folder exists or creates it. Useful for output directories
function folderExistsOrCreate(folderName){
  if(folderExists(folderName)) {
    Logger.log("Folder exists: "+ folderName);
    return true;
  }
  else {
    Logger.log("Folder does not exist: "+ folderName + ". Creating the directory.");
    DriveApp.createFolder(folderName);
    return true;
  }
}
// Checks to see if a file exists in a folder
function checkFileExists(fileName,folderName){
  let folder = DriveApp.getFoldersByName(folderName);
  if(!folder.hasNext()){
  }
  else{
    var file = folder.next().getFilesByName(fileName);
    if(!file.hasNext()){
       return true;
    }
    else{
       return false;
    }
  }
}

// Function to check if an index output sheet exists or creates it. Returns the file object
// Specify the file output name and outputdirectory
function checkIndexOutputOrCreate(fileName, folderOutput) {
  var timeZone = Session.getScriptTimeZone();
  var date = Utilities.formatDate(new Date(), timeZone, "MM-dd-yyyy hh:mm:ss");
  let file = {title: fileName, mimeType: MimeType.GOOGLE_SHEETS, parents: [{id: folderOutput.getId()}]}
  let params = "title='" + fileName + "' and parents in '" + folderOutput.getId() + "'";
  let file_search = DriveApp.searchFiles(params);
  if (file_search.hasNext()) {
    let fileId = file_search.next().getId();
    var sheet = SpreadsheetApp.openById(fileId);
    Logger.log("File index: " + fileName + " exists.");
    var sheet_index = sheet.getSheetByName("Index");
    if (sheet.getSheetByName("Backup")){
      var sheet_backup = sheet.getSheetByName("Backup");
      sheet.deleteSheet(sheet_backup);
    }
    var sheet_backup = sheet.insertSheet("Backup", 1);
    var sheet_backup_open = sheet.getSheetByName("Backup");
    sheet_index.getDataRange().copyTo(sheet_backup_open.getRange(1,1));
    if (sheet_index != null){
      sheet.deleteSheet(sheet_index);
    }
    sheet.insertSheet("Index", 0);
    sheet_index = sheet.getSheetByName("Index");
    sheet_index.addDeveloperMetadata("Date", date);
    }
  else {
    Logger.log("File index: " + fileName + " does not exist.");
    let output = Drive.Files.insert(file).id;
    var sheet = SpreadsheetApp.openById(output);
    var sheet_1 = sheet.getSheetByName("Sheet1");
    sheet.insertSheet("Index", 0);
    var sheet_index = sheet.getSheetByName("Index")
    sheet_index.addDeveloperMetadata("Date", date);
    sheet.deleteSheet(sheet_1);
  }
  return sheet;
}

// Function to convert byte array into a string
function byteToStr(byteInput){
  let signatureStr = '';
  for (i = 0; i < byteInput.length; i++) {
    let byte = byteInput[i];
    if (byte < 0)
      byte += 256;
    let byteStr = byte.toString(16);
    if (byteStr.length == 1) byteStr = '0' + byteStr;
      signatureStr += byteStr;
    }
return signatureStr;
}

// Function to remove special characters for file names
function sanitizeFileName(fileName){
  let clean_filename = fileName.replace(/\[/g, "_").replace(/\]/g, "_").replace(/\(/g, "_").replace(/\)/g, "_").replace(/^_/g, "").replace(/,/g, "_").replace(/ /g, "_").replace(/:/g, "").replace(/`/g, "").replace(/\'/g, "").replace(/&/g, "and").replace(/</g, "").replace(/>/g, "").replace(/’/g, "");
return clean_filename;
}

// Function to remove special characters for file names
function sanitizeString(string){
  let clean_string = string.replace(/\[/g, "").replace(/\]/g, "").replace(/\(/g, "").replace(/\)/g, "").replace(/^_/g, "").replace(/,/g, " ").replace(/:/g, "").replace(/`/g, "").replace(/\'/g, "").replace(/&/g, "and").replace(/</g, "").replace(/>/g, "");
return clean_string;
}

function sanitizeBody(string){
  let clean_body = string.replace(/’/g, "'").replace(/^M/g, "");
return clean_body;
}

function regexToCleanCharsMD(string){
  let clean_string = string.replace(/(\*+)(\s*\b)([^\*]+)(\b\s*)(\*+)/g, "$2$1$3$5$4");
return clean_string;
}

// Function to check if a backup sheet exists and return a hash if the file exists
// Specify the sheet name where the backup is saved, default is "Backup"
// From your backup sheet specify the column that contains the MD5 hash
// and the columns for which you return values
function returnBackupHash(sheet, sheet_name, fid, start_data_row, pos_id, pos_1_col, pos_2_col){
  if (sheet.getSheetByName(sheet_name)){
    let backup_sheet = sheet.getSheetByName(sheet_name);
    if(backup_sheet.getLastRow()> start_data_row){
      let backup_values = backup_sheet.getDataRange().getValues();
      for (let row_count = start_data_row; row_count < backup_sheet.getLastRow(); row_count++) {
        let row_id = backup_values[row_count][pos_id];
        let pos_1_value = backup_values[row_count][pos_1_col];
        //Retrieve id of existing markdown conversion
        let pos_2_value = backup_values[row_count][pos_2_col];
        if (row_id == fid){
          var results = [row_id, pos_1_value, pos_2_value];
          break;
        }
        else {
          var results = ["no_results"];
        }
      }
      return results;
    }
  }
}

// Creates a richText item with item.
function createRichText (item){
  let title = item.getName();
  let url = item.getUrl();
  let richText = SpreadsheetApp.newRichTextValue().setText(title).setLinkUrl(url).build();
  return richText;
}

// Insert a richText item in a specific cell
function insertRichText (sheetItem, item, column, row){
  let range = sheetItem.getRange(column + row);
  range.setRichTextValue(item);
}
