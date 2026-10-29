# Changelog

## [1.1.0](https://github.com/JumpToTheCloud/claude-code/compare/software-toolkit-v1.0.0...software-toolkit-v1.1.0) (2026-10-29)


### Features

* **execute-feature:** file out-of-diff review findings as bugs ([b435fee](https://github.com/JumpToTheCloud/claude-code/commit/b435fee632092619b7b99f00b125534ba4809520))
* **iteration-plan:** add execution handoff and size reconciliation ([929aee0](https://github.com/JumpToTheCloud/claude-code/commit/929aee051f8f26cb86a74604b2a86ed1f6093bce))
* **iteration-plan:** support breaking down Bug issues ([3072843](https://github.com/JumpToTheCloud/claude-code/commit/30728432403f79be8410a6022c6b0ac36e612b1d))
* **refine-story:** support refining Bug issues ([3764921](https://github.com/JumpToTheCloud/claude-code/commit/3764921ce656e412b60678421c2de97514658a77))
* **software-toolkit:** add analyze skill for spec/plan consistency ([a325ec1](https://github.com/JumpToTheCloud/claude-code/commit/a325ec190aef46624d3a495062a7b78d9777c0e5))
* **software-toolkit:** add complete-feature skill ([3704e4d](https://github.com/JumpToTheCloud/claude-code/commit/3704e4d46889d09495fc2c2d127d0895e9d052f6))
* **software-toolkit:** add constitution skill for repo setup ([f039ece](https://github.com/JumpToTheCloud/claude-code/commit/f039ece5e0e2e481fa5537b21b0bcc380fedcd97))
* **software-toolkit:** add execute-feature skill ([edebfc5](https://github.com/JumpToTheCloud/claude-code/commit/edebfc5afda0731cb72596f0e80abd9e455f3177))
* **software-toolkit:** add GitHub Project Status tracking to prd, plan, and analyze ([fd6a681](https://github.com/JumpToTheCloud/claude-code/commit/fd6a6819894b5cb772d671216bc26e7efab30119))
* **software-toolkit:** add grill-me skill to interrogate plans ([6e151ce](https://github.com/JumpToTheCloud/claude-code/commit/6e151cec72ac3b808beb1ce855cf0531812f6472))
* **software-toolkit:** add iteration-plan skill ([42143cd](https://github.com/JumpToTheCloud/claude-code/commit/42143cd2ba3af32d350074d982a0874a6735218b))
* **software-toolkit:** add plan skill for PRD technical plans ([b485709](https://github.com/JumpToTheCloud/claude-code/commit/b485709e7a41856843cc363e73cb1be8de1a6a51))
* **software-toolkit:** add prd skill to draft PRDs as GitHub issues ([76ddfb0](https://github.com/JumpToTheCloud/claude-code/commit/76ddfb08ea45011b623bbf741aa7cb16002813e7))
* **software-toolkit:** add prd-to-issues skill for PRD breakdown ([86d14a0](https://github.com/JumpToTheCloud/claude-code/commit/86d14a098f958676244e76f24c6898d3cb5e2fe6))
* **software-toolkit:** add refine-story skill ([0433dc5](https://github.com/JumpToTheCloud/claude-code/commit/0433dc5de67c9a84f2a1c739409094f27a194d34))
* **software-toolkit:** add report-bug skill ([5ad8619](https://github.com/JumpToTheCloud/claude-code/commit/5ad8619e2d0b867826b48d295230df7245d1f558))
* **software-toolkit:** add tdd skill ([9afc9a0](https://github.com/JumpToTheCloud/claude-code/commit/9afc9a0d92d7b7c5101877bd136c5f118a72b8b4))
* **software-toolkit:** auto-approve this plugin's own skill invocations ([3fc6134](https://github.com/JumpToTheCloud/claude-code/commit/3fc6134b1ae2430b6fbab3a1afcef6258a137bd5))
* **software-toolkit:** require native issue type, afk/hitl labels, milestone, and dependency links in prd-to-issues ([1ca33f6](https://github.com/JumpToTheCloud/claude-code/commit/1ca33f6fa659ebfcc1c467af7b610e6b6f06d3cb))


### Bug Fixes

* **execute-feature:** stop before claiming when nothing is executable ([c1f2a76](https://github.com/JumpToTheCloud/claude-code/commit/c1f2a765a949b7a8158b96dbaf711ed3ce486193))
* **iteration-plan:** set the parent's Component on every sub-task ([3d1ff4f](https://github.com/JumpToTheCloud/claude-code/commit/3d1ff4f8d9c2f1ebd6540f0d98774e2dee9199fe))
* **software-toolkit:** add CONSTITUTION.md to constitution lookup ([117be99](https://github.com/JumpToTheCloud/claude-code/commit/117be99a028da48afb514a97843ac718338675c0))
* **software-toolkit:** detect technical plan heading without requiring emoji ([32943d9](https://github.com/JumpToTheCloud/claude-code/commit/32943d978ae4e006055f33bad10fe2b3df85b4f8))


### Documentation

* **conventional-commits:** forbid AI attribution in any repository ([509a1a8](https://github.com/JumpToTheCloud/claude-code/commit/509a1a8f1d310d78a7d829e2e86a62f564e9cf12))
* **execute-feature:** hand the Done status off to complete-feature ([397ec0e](https://github.com/JumpToTheCloud/claude-code/commit/397ec0eb81d6735ba2e10ef6c61cc8c085688878))
* **iteration-plan:** point execution handoff to /execute-feature ([8f14717](https://github.com/JumpToTheCloud/claude-code/commit/8f14717a599387d3ec06dfc2ed5aac3006dc1af6))
* **prd-to-issues:** clarify execution-phase handoff comments ([bdfe26e](https://github.com/JumpToTheCloud/claude-code/commit/bdfe26e9efa2e0af14b418458ec8375832576448))
* **prd-to-issues:** document execute-feature setup requirements ([96d073c](https://github.com/JumpToTheCloud/claude-code/commit/96d073c2ba5c5c6030a5ad087e4815e1c266fc6a))
* **prd-to-issues:** document the Bug, Released and complete-feature setup ([6036127](https://github.com/JumpToTheCloud/claude-code/commit/603612735edce354f885e15d023cc04beead4641))
* **refine-story:** ban Epic wording, pin coverage section title ([d0d5e68](https://github.com/JumpToTheCloud/claude-code/commit/d0d5e680ceddb157af97e5d3a4b4375238ee24a1))
* **software-toolkit:** describe prd workflow in plugin manifest ([f2242c3](https://github.com/JumpToTheCloud/claude-code/commit/f2242c323fc6cac2018135163c4c211616d0e445))
* **software-toolkit:** document refine-story and iteration-plan setup ([115aa0c](https://github.com/JumpToTheCloud/claude-code/commit/115aa0c20dc3a0d6f934344879ffabd8f66585c7))
* **software-toolkit:** update /constitution references to /init-repo ([dfc0d41](https://github.com/JumpToTheCloud/claude-code/commit/dfc0d41bfcac5310e4233cbb49f7f8b3f1768e90))
* **tdd:** define unattended behavior for task-executor runs ([a20dd9e](https://github.com/JumpToTheCloud/claude-code/commit/a20dd9edc41d7218102a46b322eb2a91a37492cc))


### Code Refactoring

* **software-toolkit:** rename constitution skill to init-repo ([a4c025a](https://github.com/JumpToTheCloud/claude-code/commit/a4c025ab1389bd942cafad0c5dd3a0e2df068345))


### Miscellaneous

* **software-toolkit:** bump plugin version to 1.1.0 ([b0ec89a](https://github.com/JumpToTheCloud/claude-code/commit/b0ec89af78890cb2478a4be69ba62b184ae6335c))
* **software-toolkit:** bump plugin version to 1.4.0 ([4abd091](https://github.com/JumpToTheCloud/claude-code/commit/4abd0912f3e4b22273af9606efa7da4e4a85bd51))
* **software-toolkit:** list new skills in the plugin description ([ae18a39](https://github.com/JumpToTheCloud/claude-code/commit/ae18a3978a3406c5e68a53dd2f8b4bfc46890118))

## 1.0.0 (2026-08-08)


### Features

* **software-toolkit:** add conventional-commits skill and agent ([5323764](https://github.com/cdk-x/claude-code/commit/5323764104fd77b1aca999542feccf8133643aff))


### Documentation

* **software-toolkit:** forbid AI co-author trailers explicitly ([275b2f5](https://github.com/cdk-x/claude-code/commit/275b2f59c2713d9a22f71a41e4814d2c6144ce51))
