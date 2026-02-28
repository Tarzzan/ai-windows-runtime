#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TelemetryStage {
    Start,
    Success,
    Error,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RuntimeTelemetryEvent {
    pub seq: u64,
    pub component: String,
    pub action: String,
    pub stage: TelemetryStage,
    pub detail: Option<String>,
}

#[derive(Debug, Default)]
pub struct TelemetryRecorder {
    next_seq: u64,
    events: Vec<RuntimeTelemetryEvent>,
}

impl TelemetryRecorder {
    pub fn new() -> Self {
        Self {
            next_seq: 1,
            events: Vec::new(),
        }
    }

    fn record(
        &mut self,
        component: &str,
        action: &str,
        stage: TelemetryStage,
        detail: Option<String>,
    ) {
        let event = RuntimeTelemetryEvent {
            seq: self.next_seq,
            component: component.to_string(),
            action: action.to_string(),
            stage,
            detail,
        };
        self.next_seq = self.next_seq.saturating_add(1);
        self.events.push(event);
    }

    pub fn record_start(&mut self, component: &str, action: &str) {
        self.record(component, action, TelemetryStage::Start, None);
    }

    pub fn record_success(&mut self, component: &str, action: &str, detail: Option<String>) {
        self.record(component, action, TelemetryStage::Success, detail);
    }

    pub fn record_error(&mut self, component: &str, action: &str, detail: impl Into<String>) {
        self.record(
            component,
            action,
            TelemetryStage::Error,
            Some(detail.into()),
        );
    }

    pub fn events(&self) -> &[RuntimeTelemetryEvent] {
        &self.events
    }

    pub fn take_events(&mut self) -> Vec<RuntimeTelemetryEvent> {
        std::mem::take(&mut self.events)
    }

    pub fn clear(&mut self) {
        self.events.clear();
    }
}

#[cfg(test)]
mod tests {
    use super::{TelemetryRecorder, TelemetryStage};

    #[test]
    fn recorder_tracks_sequenced_events() {
        let mut recorder = TelemetryRecorder::new();
        recorder.record_start("win32", "CreateProcessW");
        recorder.record_success("win32", "CreateProcessW", Some("pid=1000".to_string()));
        recorder.record_error("win32", "CreateThread", "invalid process handle");

        let events = recorder.events();
        assert_eq!(events.len(), 3);
        assert_eq!(events[0].seq, 1);
        assert_eq!(events[0].stage, TelemetryStage::Start);
        assert_eq!(events[1].seq, 2);
        assert_eq!(events[1].stage, TelemetryStage::Success);
        assert_eq!(events[2].seq, 3);
        assert_eq!(events[2].stage, TelemetryStage::Error);
    }
}
