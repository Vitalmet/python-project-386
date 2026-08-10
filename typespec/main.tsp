import "@typespec/http";
import "@typespec/openapi3";

import "./models.tsp";
import "./operations.tsp";

using TypeSpec.Http;

@doc("API приложения «Календарь звонков»: бронирование звонков гостями на 14 дней вперёд.")
@service(#{ title: "Календарь звонков" })
@server(
  "http://localhost:5000",
  "Локальный сервер разработки (Flask)",
)
namespace CallCalendar {}
