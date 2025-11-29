---
name: llm4s-scala
description: LLM4S Scala functional LLM interfaces with Effect system integration. Use when building LLM applications in Scala with ZIO or Cats Effect, implementing type-safe AI pipelines with functional error handling, creating composable prompt systems in Scala, or leveraging Scala's type system for robust AI applications.
---

# LLM4S Scala Functional LLM Interfaces

Functional LLM programming in Scala with categorical effect systems.

## Installation

```scala
// build.sbt
libraryDependencies ++= Seq(
  "dev.zio" %% "zio" % "2.0.19",
  "dev.zio" %% "zio-json" % "0.6.2",
  "org.typelevel" %% "cats-effect" % "3.5.2",
  "co.fs2" %% "fs2-core" % "3.9.3"
)
```

## Core Abstractions

### LLM as Effect

```scala
import zio._
import zio.json._

// LLM call as effectful operation
trait LLMClient {
  def complete(request: CompletionRequest): Task[CompletionResponse]
  def stream(request: CompletionRequest): ZStream[Any, Throwable, String]
}

case class CompletionRequest(
  model: String,
  messages: List[Message],
  temperature: Double = 0.7,
  maxTokens: Option[Int] = None
)

case class Message(role: String, content: String)

case class CompletionResponse(
  id: String,
  content: String,
  usage: Usage
)

case class Usage(promptTokens: Int, completionTokens: Int)

// JSON codecs
implicit val messageCodec: JsonCodec[Message] = DeriveJsonCodec.gen
implicit val requestCodec: JsonCodec[CompletionRequest] = DeriveJsonCodec.gen
implicit val responseCodec: JsonCodec[CompletionResponse] = DeriveJsonCodec.gen
```

### OpenAI Client Implementation

```scala
import zio.http._

class OpenAIClient(apiKey: String) extends LLMClient {
  private val baseUrl = "https://api.openai.com/v1"
  
  override def complete(request: CompletionRequest): Task[CompletionResponse] = {
    for {
      response <- Client.request(
        Request.post(
          URL.decode(s"$baseUrl/chat/completions").toOption.get,
          Body.fromString(request.toJson)
        ).addHeader(Header.Authorization.Bearer(apiKey))
         .addHeader(Header.ContentType(MediaType.application.json))
      ).provide(Client.default)
      
      body <- response.body.asString
      result <- ZIO.fromEither(body.fromJson[CompletionResponse])
                   .mapError(e => new Exception(s"Parse error: $e"))
    } yield result
  }
  
  override def stream(request: CompletionRequest): ZStream[Any, Throwable, String] = {
    // Streaming implementation
    ZStream.fromZIO(complete(request)).map(_.content)
  }
}

object OpenAIClient {
  val layer: ZLayer[Any, Nothing, LLMClient] = ZLayer.succeed {
    new OpenAIClient(sys.env("OPENAI_API_KEY"))
  }
}
```

## Categorical Patterns

### Prompt as Functor

```scala
import cats._
import cats.implicits._

// Prompt template with functor instance
case class Prompt[A](template: String, extract: String => A) {
  def render(vars: Map[String, String]): String =
    vars.foldLeft(template) { case (t, (k, v)) => 
      t.replace(s"{$k}", v) 
    }
}

implicit val promptFunctor: Functor[Prompt] = new Functor[Prompt] {
  def map[A, B](fa: Prompt[A])(f: A => B): Prompt[B] =
    Prompt(fa.template, s => f(fa.extract(s)))
}

// Usage
val sentimentPrompt: Prompt[String] = Prompt(
  "Analyze sentiment of: {text}\nSentiment:",
  identity
)

val scoredPrompt: Prompt[Int] = sentimentPrompt.map {
  case "positive" => 1
  case "negative" => -1
  case _ => 0
}
```

### LLM Monad Transformer

```scala
import cats.effect._
import cats.data._

// LLM effect as monad transformer
type LLMIO[A] = ReaderT[IO, LLMClient, A]

object LLMIO {
  def complete(request: CompletionRequest): LLMIO[CompletionResponse] =
    ReaderT(client => IO.fromFuture(IO(client.complete(request))))
  
  def ask[A](prompt: String)(extract: String => A): LLMIO[A] =
    complete(CompletionRequest(
      model = "gpt-4o",
      messages = List(Message("user", prompt))
    )).map(r => extract(r.content))
  
  def pure[A](a: A): LLMIO[A] = ReaderT.pure(a)
}

// Monadic composition
val pipeline: LLMIO[(String, List[String])] = for {
  summary <- LLMIO.ask("Summarize this document...")(identity)
  keywords <- LLMIO.ask(s"Extract keywords from: $summary")(
    _.split(",").toList.map(_.trim)
  )
} yield (summary, keywords)
```

### Kleisli Composition

```scala
import cats.data.Kleisli
import cats.effect.IO

type LLMKleisli[A, B] = Kleisli[IO, A, B]

// Composable LLM operations
def classify(text: String): IO[String] = IO.pure("positive")
def elaborate(category: String): IO[String] = IO.pure(s"Details about $category")
def format(details: String): IO[String] = IO.pure(s"Formatted: $details")

val classifyK: LLMKleisli[String, String] = Kleisli(classify)
val elaborateK: LLMKleisli[String, String] = Kleisli(elaborate)
val formatK: LLMKleisli[String, String] = Kleisli(format)

// Compose: classify >>> elaborate >>> format
val pipeline: LLMKleisli[String, String] = 
  classifyK >>> elaborateK >>> formatK

// Run
val result: IO[String] = pipeline.run("input text")
```

## ZIO Integration

### ZIO Service Pattern

```scala
import zio._

// LLM as ZIO service
trait LLMService {
  def generate(prompt: String): Task[String]
  def generateStructured[A: JsonDecoder](prompt: String): Task[A]
  def streamGenerate(prompt: String): ZStream[Any, Throwable, String]
}

object LLMService {
  def generate(prompt: String): ZIO[LLMService, Throwable, String] =
    ZIO.serviceWithZIO[LLMService](_.generate(prompt))
    
  def generateStructured[A: JsonDecoder](prompt: String): ZIO[LLMService, Throwable, A] =
    ZIO.serviceWithZIO[LLMService](_.generateStructured[A](prompt))
}

// Implementation
case class LLMServiceLive(client: LLMClient) extends LLMService {
  override def generate(prompt: String): Task[String] =
    client.complete(CompletionRequest(
      model = "gpt-4o",
      messages = List(Message("user", prompt))
    )).map(_.content)
    
  override def generateStructured[A: JsonDecoder](prompt: String): Task[A] =
    generate(prompt).flatMap { content =>
      ZIO.fromEither(content.fromJson[A])
         .mapError(e => new Exception(s"Parse error: $e"))
    }
    
  override def streamGenerate(prompt: String): ZStream[Any, Throwable, String] =
    client.stream(CompletionRequest(
      model = "gpt-4o",
      messages = List(Message("user", prompt))
    ))
}

object LLMServiceLive {
  val layer: ZLayer[LLMClient, Nothing, LLMService] =
    ZLayer.fromFunction(LLMServiceLive(_))
}
```

### Error Handling

```scala
// Typed errors
sealed trait LLMError
case class RateLimitError(retryAfter: Int) extends LLMError
case class InvalidRequestError(message: String) extends LLMError
case class ModelError(message: String) extends LLMError

// Error-aware operations
def safeGenerate(prompt: String): ZIO[LLMService, LLMError, String] =
  LLMService.generate(prompt)
    .mapError {
      case e if e.getMessage.contains("rate_limit") => 
        RateLimitError(60)
      case e if e.getMessage.contains("invalid") => 
        InvalidRequestError(e.getMessage)
      case e => 
        ModelError(e.getMessage)
    }

// Retry with typed errors
def withRetry(prompt: String): ZIO[LLMService, LLMError, String] =
  safeGenerate(prompt).retry(
    Schedule.recurs(3) && Schedule.exponential(1.second)
  )
```

## Streaming with FS2

```scala
import fs2._
import cats.effect._

// Streaming LLM responses
def streamCompletion(prompt: String): Stream[IO, String] = {
  Stream.eval(IO.pure(prompt))
    .through(tokenize)
    .through(generateTokens)
}

def tokenize: Pipe[IO, String, String] =
  _.flatMap(s => Stream.emits(s.split(" ")))

def generateTokens: Pipe[IO, String, String] =
  _.evalMap(token => IO.sleep(50.millis) *> IO.pure(s"$token "))

// Consume stream
val program: IO[Unit] = 
  streamCompletion("Hello world")
    .evalMap(token => IO(print(token)))
    .compile
    .drain
```

## Tool Integration

```scala
// Tool definition
case class Tool[A, B](
  name: String,
  description: String,
  execute: A => Task[B]
)

// Tool-augmented LLM
trait ToolAugmentedLLM {
  def generateWithTools[A: JsonDecoder](
    prompt: String,
    tools: List[Tool[_, _]]
  ): Task[A]
}

// Example tools
val searchTool = Tool[String, List[String]](
  name = "search",
  description = "Search the web",
  execute = query => ZIO.succeed(List(s"Result for: $query"))
)

val calculatorTool = Tool[String, Double](
  name = "calculate",
  description = "Evaluate math expression",
  execute = expr => ZIO.attempt(/* safe eval */ 0.0)
)
```

## Categorical Guarantees

LLM4S provides:

1. **Effect Safety**: All LLM calls wrapped in IO/Task
2. **Composability**: Kleisli/ReaderT for pipeline composition  
3. **Type Safety**: JSON codecs ensure structured output types
4. **Error Handling**: Typed errors with ZIO/Cats Effect
5. **Streaming**: FS2/ZStream for token-by-token processing
