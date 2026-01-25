# MalURLBench: A Benchmark Evaluating Agents' Vulnerabilities When Processing Web URLs

## Background and Motivation

LLM-based web agents have attracted considerable interest in recent years. However, web agents greatly enlarge the attack surface. The first reason is the extremely complex structure of webpages; The second reason is that webpages are multimodal. These characteristics make webpages a good attack vector to damage the service provider.

As shown in the following figure, web agents' workflow is two-staged. First, as the brain of web agents, LLMs need to determine whether to accept a URL. Second, once this URL is accepted, the LLM invokes tools to visit the corresponding webpages and parse the content. As the beginning of the entire workflow, the security of stage 1 is of vital importance. **Only after agents are induced to trust a malicious URL can attackers use the webpage to launch more attacks**. **However, there have not been benchmarks evaluating the first stage's security**. Therefore, this paper aims to evaluate the security problems in stage 1.
