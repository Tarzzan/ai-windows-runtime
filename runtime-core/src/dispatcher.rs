use std::collections::HashMap;
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ApiStatus {
    Implemented,
    Stubbed,
    Missing,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DispatchDecision {
    pub api: String,
    pub status: ApiStatus,
    pub detail: Option<String>,
}

#[derive(Debug, Clone)]
enum ApiSpec {
    Implemented,
    Stubbed(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DispatchError {
    MissingApi(String),
}

impl fmt::Display for DispatchError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::MissingApi(name) => write!(f, "missing API implementation: {name}"),
        }
    }
}

impl std::error::Error for DispatchError {}

#[derive(Debug, Default)]
pub struct ApiDispatcher {
    registry: HashMap<String, ApiSpec>,
}

impl ApiDispatcher {
    pub fn new() -> Self {
        Self {
            registry: HashMap::new(),
        }
    }

    pub fn register_implemented(&mut self, api: &str) {
        self.registry.insert(api.to_string(), ApiSpec::Implemented);
    }

    pub fn register_stub(&mut self, api: &str, reason: &str) {
        self.registry
            .insert(api.to_string(), ApiSpec::Stubbed(reason.to_string()));
    }

    pub fn resolve(&self, api: &str) -> DispatchDecision {
        match self.registry.get(api) {
            Some(ApiSpec::Implemented) => DispatchDecision {
                api: api.to_string(),
                status: ApiStatus::Implemented,
                detail: None,
            },
            Some(ApiSpec::Stubbed(reason)) => DispatchDecision {
                api: api.to_string(),
                status: ApiStatus::Stubbed,
                detail: Some(reason.clone()),
            },
            None => DispatchDecision {
                api: api.to_string(),
                status: ApiStatus::Missing,
                detail: Some("no registered implementation".to_string()),
            },
        }
    }

    pub fn call(&self, api: &str) -> Result<DispatchDecision, DispatchError> {
        let decision = self.resolve(api);
        if decision.status == ApiStatus::Missing {
            return Err(DispatchError::MissingApi(api.to_string()));
        }
        Ok(decision)
    }
}

#[cfg(test)]
mod tests {
    use super::{ApiDispatcher, ApiStatus, DispatchError};

    #[test]
    fn resolves_implemented_api() {
        let mut d = ApiDispatcher::new();
        d.register_implemented("kernel32.GetLastError");
        let decision = d.resolve("kernel32.GetLastError");
        assert_eq!(decision.status, ApiStatus::Implemented);
    }

    #[test]
    fn resolves_stubbed_api() {
        let mut d = ApiDispatcher::new();
        d.register_stub("winhttp.WinHttpOpen", "placeholder during bootstrap");
        let decision = d.resolve("winhttp.WinHttpOpen");
        assert_eq!(decision.status, ApiStatus::Stubbed);
        assert_eq!(
            decision.detail.as_deref(),
            Some("placeholder during bootstrap")
        );
    }

    #[test]
    fn call_fails_for_missing_api() {
        let d = ApiDispatcher::new();
        let err = d
            .call("combase.RoActivateInstance")
            .expect_err("missing APIs must fail");
        assert_eq!(
            err,
            DispatchError::MissingApi("combase.RoActivateInstance".to_string())
        );
    }
}
