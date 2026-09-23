import io.gatling.core.Predef._
import io.gatling.http.Predef._
import scala.concurrent.duration._

class InternetBankingLoginSimulation extends Simulation {

  // Configuration parameters
  val baseUrl = System.getProperty("baseUrl", "http://localhost:8080")
  val loginEndpoint = "/api/login"
  val username = System.getProperty("username", "testUser")
  val password = System.getProperty("password", "testPassword")

  // HTTP protocol configuration
  val httpProtocol = http
    .baseUrl(baseUrl)
    .acceptHeader("application/json")
    .contentTypeHeader("application/json")

  // Scenario definition
  val scn = scenario("Internet Banking Login Scenario")
    .exec(http("Login Request")
      .post(loginEndpoint)
      .body(StringBody(s"""{"username": "$username", "password": "$password"}""")).asJson
      .check(status.is(200))
      .check(jsonPath("$.token").exists)
    )

  // Load simulation
  setUp(
    scn.inject(atOnceUsers(100)) // Adjust the number of users as needed
  ).protocols(httpProtocol)
}