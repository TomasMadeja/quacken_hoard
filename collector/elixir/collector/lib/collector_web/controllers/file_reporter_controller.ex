defmodule CollectorWeb.FileReporterController do
  use CollectorWeb, :controller

  def fileUpload(conn, %{"id" => hostID, "cap" => capFile}) do
    if File.exists?(capFile.path) do
      path = "collectionStorage/#{hostID}"
      f_path = "#{path}/#{Path.rootname(capFile.filename)}_#{inspect(:os.system_time)}#{Path.extname(capFile.filename)}"
      File.mkdir_p!(path)
      File.cp!(capFile.path, f_path)
    end
    conn
    |> put_status(202)
    |> text("OK")
  end

end
