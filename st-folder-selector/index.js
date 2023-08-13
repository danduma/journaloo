import React, { useState } from "react";
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib";

const FolderSelector = (props) => {
  const [selectedFolder, setSelectedFolder] = useState(null);

  const handleFolderChange = (event) => {
    if (event.target.files.length > 0) {
      const folderPath = event.target.files[0].webkitRelativePath;
      const folderName = folderPath.split("/")[0];
      setSelectedFolder(folderName);
      Streamlit.setComponentValue(folderName);
    }
  };

  return (
    <div>
      <input
        type="file"
        directory="" webkitdirectory=""
        onChange={handleFolderChange}
      />
      {selectedFolder && <p>Selected Folder: {selectedFolder}</p>}
    </div>
  );
};

export default withStreamlitConnection(FolderSelector);
