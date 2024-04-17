
/**
 * Copyright 2024 Jason
 */

/**
 *@brief Returns comment prefixes for various file types.
 *@param	fileType   The file type to get comment prefix for
 *@return	Comment prefix for the specified file type or `//` if the file type is unknown
*/
export function getCommentprefixes(fileType: string): string {
  switch (fileType) {
    case "python":
      return "# ";
    case "javascript":
      return "// ";
    case "html":
      return "<!-- -->";
    case "css":
      return "/* */";
    case "cpp":
    case "c":
    case "h": // C/C++ header
    case "java":
    case "csharp":
      return "// ";
    default:
      return "//"; // No comment prefix for unknown file types
  }
}