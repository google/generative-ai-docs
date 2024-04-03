//Code comment: (generated)
//Given a file type, returns the comment prefix appropriate for that file type.
//@param {string} fileType The file type to get the comment prefix for.
//@returns {string} The comment prefix for the given file type.
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

// TODO(you!): Support doxygen comment styles.