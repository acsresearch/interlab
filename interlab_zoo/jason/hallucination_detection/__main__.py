import logging
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

from interlab.context import Context, FileStorage
from interlab.utils.hydra_logs import log_exceptions
from interlab_zoo.jason.hallucination_detection.utils import Result, get_engine

LOGGER = logging.getLogger(__name__)


HALLUCINATION_PROMPT = """
Tristan Rogers (born 3 June 1946) is an Australian actor. He is best known for his roles as 
"""

FACTUAL_COMPLETION = """
Robert Scorpio on the American daytime soap opera General Hospital, and as Colin Atkinson on the Australian soap opera The Young Doctors.\n\nRogers was born in Melbourne, Australia. He began his career in the early 1970s, appearing in the Australian television series Homicide and Division 4. In 1976, he moved to the United States and began appearing in American television series, including The Rockford Files, Charlie's Angels, and Fantasy Island.\n\nIn 1980, Rogers joined the cast of General Hospital as Robert Scorpio, a role he played until 1992. He returned to the show in 1995 and has been playing the role ever since. He also appeared in the spin-off series General Hospital: Night Shift.\n\nIn addition to his work on General Hospital, Rogers has appeared in a number of other television series, including The Bold and the Beautiful, The Young and the Restless, and The Bay. He has also appeared in films such as The Perfect Storm and The Scorpion King.
"""

JUDGE_PROMPT = """
Answer "factual" if the following completions convey mostly the same information, and "hallucinated" otherwise.
Do not include any other information except for "factual" or "hallucinated" in your answer.

The completions:

"""

# tested in playground that
# - text-davinci-003 completes correctly whereas
# - text-curie-001 gives random but nice-sounding completions


@hydra.main(version_base="1.2", config_path="conf", config_name="main")
@log_exceptions(LOGGER)
def main(cfg: DictConfig):
    """
    Basic idea:
    1) Prompt for completion n times
    2) Have a judge model rule whether the completions convey the same information
    ==> interpretation: not hallucinated
    3) Have a judge model rule whether any of the completion conveys the same information as the true completion.

    Technicalities:
    - limit number of tokens in completion to sth small to exclude irrelevant extra info
    """
    storage = FileStorage(
        Path.cwd()
    )  # Directory for storing contexts (structured logs)
    LOGGER.info(storage.directory)

    # todo: replace with bare langchain models and use it inside a `query_model` call
    subject = get_engine(cfg.subject)
    judge = get_engine(cfg.judge)

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    with Context(f"hallucination-detection", storage=storage, inputs=cfg_dict) as c:
        with Context("completions"):
            completions = []
            for i in range(cfg.n):
                with Context(f"completion-{i}") as completion_context:
                    completion = subject(HALLUCINATION_PROMPT, max_tokens=100)
                    completions.append(completion)
                    completion_context.set_result(completion)

        with Context("judgement") as judgement_context:
            verdict = judge(JUDGE_PROMPT + "\n".join(completions), max_tokens=100)
            judgement_context.set_result(verdict)

    c.set_result(
        Result(
            completions=completions,
            verdict=verdict,
        )
    )


if __name__ == "__main__":
    main()
