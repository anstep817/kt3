import { useState } from "react";
import axios from "axios";

function ImageUpload() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function handleChange(e) {
    const selected = e.target.files[0];
    if (!selected) {
      return;
    }
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setProgress(0);
    setResult(null);
    setError("");
  }

  async function handleUpload() {
    if (!file) {
      setError("Сначала выберите файл");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setError("");
    setResult(null);
    setProgress(0);

    try {
      const response = await axios.post("http://localhost:8000/upload-image/", formData, {
        onUploadProgress: (e) => {
          if (e.total) {
            const percent = Math.round((e.loaded * 100) / e.total);
            setProgress(percent);
          }
        },
      });
      setResult(response.data);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Не удалось подключиться к серверу");
      }
    }
  }

  return (
    <div className="uploader">
      <input type="file" accept="image/*" onChange={handleChange} />

      {preview && (
        <div className="block">
          <h3>Предпросмотр</h3>
          <img src={preview} alt="preview" className="preview" />
        </div>
      )}

      <button onClick={handleUpload}>Загрузить на сервер</button>

      <div className="block">
        <progress value={progress} max="100"></progress>
        <span> {progress}%</span>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="block">
          <h3>Миниатюра с сервера</h3>
          <img src={result.thumbnail_url} alt="thumbnail" />
          <p>
            Оригинал {result.width}x{result.height}:{" "}
            <a href={result.original_url} target="_blank">
              {result.original_url}
            </a>
          </p>
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
