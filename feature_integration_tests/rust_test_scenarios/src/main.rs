mod internals;
mod scenarios;

use internals::helpers::monotonic_clock::MonotonicClockTime;
use internals::test_context::TestContext;
use scenarios::RootScenarioGroup;

use clap::{Parser, ValueEnum};
use std::io;

use tracing::Level;
use tracing_subscriber::FmtSubscriber;

#[derive(ValueEnum, Debug, Clone, PartialEq, Eq)]
enum InputType {
    Stdin,
    Arg,
}

#[derive(Parser, Debug)]
pub struct Args {
    #[arg(short, long, default_value_t = String::from(""))]
    name: String,

    #[arg(short, long)]
    input: Option<String>,

    #[arg(long, value_enum, default_value_t = InputType::Stdin)]
    input_type: InputType,

    #[arg(long, help = "List all available scenarios")]
    list_scenarios: bool,
}

fn read_test_stdin_input() -> String {
    println!("Please enter the TestInput in JSON format or press ENTER for default:");
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer).unwrap();
    let trimmed = buffer.trim();
    if trimmed.is_empty() {
        // Default value if input is empty
        // This is enough for most tests but not all
        r#"{"runtime": {"task_queue_size": 256, "workers": 4}}"#.to_string()
    } else {
        trimmed.to_string()
    }
}

fn init_tracing_subscriber() {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::TRACE)
        .with_thread_ids(true)
        .with_timer(MonotonicClockTime::new())
        .json()
        .finish();

    tracing::subscriber::set_global_default(subscriber)
        .expect("Setting default subscriber failed!");
}

fn main() {
    let arguments = Args::parse();
    let mut context = TestContext::new(Box::new(RootScenarioGroup::new()));

    if arguments.list_scenarios {
        context.list_scenarios();
        return;
    }

    if arguments.name.is_empty() {
        panic!("Scenario name must be provided.");
    }

    let mut input = arguments.input.clone();
    if arguments.input_type == InputType::Stdin {
        input = Some(read_test_stdin_input());
    }

    init_tracing_subscriber();
    context.run_scenario(arguments.name.as_str(), input);
}
