//! Scouting probe: does the production HTTP path actually capture logprobs
//! from a DOCUMENTED OpenAI-compatible chat-completion response?
use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;

use fleet_resonance::probe::OpenAICompatibleClient;
use fleet_resonance::ProbeConfig;

// Shape per OpenAI's Chat Completions API reference:
//   choices[0].logprobs = object { content: array of {token,bytes,logprob,top_logprobs}, refusal }
const BODY: &str = r#"{"id":"x","object":"chat.completion","created":1,"model":"glm-5.1","choices":[{"index":0,"message":{"role":"assistant","content":"hello world"},"finish_reason":"stop","logprobs":{"content":[{"token":"hello","bytes":[104],"logprob":-0.1,"top_logprobs":[]},{"token":" world","bytes":[32],"logprob":-0.5,"top_logprobs":[]}],"refusal":null}}],"usage":{"prompt_tokens":1,"completion_tokens":2,"total_tokens":3}}"#;

#[test]
fn production_path_captures_logprobs_from_a_real_api_response() {
    let listener = TcpListener::bind("127.0.0.1:0").unwrap();
    let addr = listener.local_addr().unwrap();
    thread::spawn(move || {
        let (mut stream, _) = listener.accept().unwrap();
        let mut buf = [0u8; 8192];
        let _ = stream.read(&mut buf);
        let resp = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            BODY.len(), BODY);
        let _ = stream.write_all(resp.as_bytes());
        let _ = stream.flush();
    });

    let client = OpenAICompatibleClient::new(
        format!("http://{}", addr), "sk-test".to_string(), "glm-5.1".to_string());
    let resp = client
        .blocking_generate("hi", Some(7), &ProbeConfig::default())
        .unwrap_or_else(|e| panic!("request failed: {}", e));

    println!("PARSE_RESULT content={:?} logprobs={:?} token_probs={:?}",
             resp.content, resp.logprobs, resp.token_probs);

    assert_eq!(resp.content, "hello world", "body should still parse");
    assert_eq!(resp.logprobs.len(), 2,
        "expected 2 logprobs from a documented OpenAI-compatible response, got {}", resp.logprobs.len());
    assert_eq!(resp.token_probs.len(), 2, "expected 2 token probs, got {}", resp.token_probs.len());
}
