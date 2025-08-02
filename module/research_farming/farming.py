from module.base.utils import color_bar_percentage
from module.config.deep import deep_get
from module.logger import logger
from module.base.base import ModuleBase
from module.ui.ui import UI
from module.ui.page import page_shipyard
from module.shipyard.shipyard_reward import RewardShipyard
from module.research_farming.assets import (SHIP_EXPERIENCE_PERCENT_1, SHIP_EXPERIENCE_PERCENT_2,
                                            SHIP_EXPERIENCE_FINISHED_1, SHIP_EXPERIENCE_FINISHED_2,
                                            SHIP_EXPERIENCE_COMPLETE_1, SHIP_EXPERIENCE_COMPLETE_2,
                                            SHIP_EXPERIENCE_COMMIT_1, SHIP_EXPERIENCE_COMMIT_2)
from datetime import datetime


class ExpHasFinished(Exception):
    ...


class ExpFinished(Exception):
    ...


class ExpNotFinished(Exception):
    ...


class ResearchFarming(UI, ModuleBase):
    def _DisableAllResearchFarmTask(self):
        for i in range(1, 7):
            self.config.modified[f"{self._GetResearchFarmTaskName(i)}.Scheduler.Enable"] = False
        self.config.modified["ResearchFarmingSetting.OpsiHazard1ResearchFarming.Enable"] = False
        self.config.save(self.config.config_name)

    def _Override(self, Index):
        if Index == 1:
            self.SHIP_EXPERIENCE_PERCENT = SHIP_EXPERIENCE_PERCENT_1
            self.SHIP_EXPERIENCE_FINISHED = SHIP_EXPERIENCE_FINISHED_1
            self.SHIP_EXPERIENCE_COMPLETE = SHIP_EXPERIENCE_COMPLETE_1
            self.SHIP_EXPERIENCE_COMMIT = SHIP_EXPERIENCE_COMMIT_1
        elif Index == 2:
            self.SHIP_EXPERIENCE_PERCENT = SHIP_EXPERIENCE_PERCENT_2
            self.SHIP_EXPERIENCE_FINISHED = SHIP_EXPERIENCE_FINISHED_2
            self.SHIP_EXPERIENCE_COMPLETE = SHIP_EXPERIENCE_COMPLETE_2
            self.SHIP_EXPERIENCE_COMMIT = SHIP_EXPERIENCE_COMMIT_2

    def _UiGotoTargetShip(self):
        self.ui_goto(page_shipyard)
        Series = deep_get(self.config.data, "ResearchFarmingSetting.ResearchFarmingSetting.ResearchSeries")
        Index = deep_get(self.config.data, "ResearchFarmingSetting.ResearchFarmingSetting.ShipIndex")
        RewardShipyard(config=self.config, device=self.device).shipyard_set_focus(series=Series, index=Index)

    def _IsSingleFinished(self, Index):
        self._Override(Index)

        if self.appear(self.SHIP_EXPERIENCE_COMPLETE, threshold=64):
            logger.info(f"ship's exp {Index} has completed")
            raise ExpHasFinished

        CurrentPercent = color_bar_percentage(self.device.image, self.SHIP_EXPERIENCE_PERCENT.area, prev_color=(255, 239, 82))
        if CurrentPercent > 0.99 and self.appear(self.SHIP_EXPERIENCE_FINISHED):
            logger.info(f"commit ship's exp {Index}")
            self.ui_click(self.SHIP_EXPERIENCE_FINISHED, check_button=self.SHIP_EXPERIENCE_COMMIT)
            self.device.sleep(0.5)
            self.device.click(self.SHIP_EXPERIENCE_COMMIT)
            raise ExpFinished

        self.config.modified["Dashboard.ResearchPercent.Value"] = int(CurrentPercent * 100)
        self.config.modified["Dashboard.ResearchPercent.Record"] = datetime.now().replace(microsecond=0)

        raise ExpNotFinished

    def _Notify(self, Index):
        IsPush = deep_get(self.config.data, "ResearchFarmingSetting.ResearchFarmingSetting.OnepushNotify")
        if IsPush:
            from module.notify import handle_notify
            handle_notify(self.config.Error_OnePushConfig,
                          title=f"Alas <{self.config.config_name}>: Research ship's experience finished",
                          content=f"Ship's experience {Index} has finished")

    def CheckResearchShipExperience(self):
        self.device.screenshot()
        self._UiGotoTargetShip()
        ExperienceIndex = deep_get(self.config.data, "ResearchFarmingSetting.ResearchFarmingSetting.ExperienceIndex")
        if ExperienceIndex == 1 or ExperienceIndex == 2:
            try:
                self._IsSingleFinished(ExperienceIndex)
            except (ExpHasFinished, ExpFinished):
                self._DisableAllResearchFarmTask()
                self._Notify(ExperienceIndex)
            except ExpNotFinished:
                return
        elif ExperienceIndex == 0:
            try:
                self._IsSingleFinished(1)
            except ExpHasFinished:
                pass
            except ExpFinished:
                self._Notify(1)
                return
            except ExpNotFinished:
                return

            try:
                self._IsSingleFinished(2)
            except (ExpHasFinished, ExpFinished):
                self._DisableAllResearchFarmTask()
                self._Notify(2)
            except ExpNotFinished:
                return

    def _GetResearchFarmTaskName(self, Index):
        return f"ResearchFarm{Index if Index != 1 else ''}"

    def _SetOilLimit(self, Index):
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.StopCondition.OilLimit"] = self.config.ResearchFarmingSetting_OilLimit

    def _SetCampaign(self, Index):
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Campaign.Name"] = deep_get(self.config.data,
                                                                                                 f"ResearchFarmingSetting.ResearchFarm{Index}Setting.Campaign")

    def _SetFleet(self, Index):
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Fleet.Fleet1"] = deep_get(self.config.data,
                                                                                                f"ResearchFarmingSetting.ResearchFarm{Index}Setting.Fleet1")
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Fleet.Fleet2"] = deep_get(self.config.data,
                                                                                                f"ResearchFarmingSetting.ResearchFarm{Index}Setting.Fleet2")
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Fleet.FleetOrder"] = "fleet1_all_fleet2_standby"

    def _SetEmotion(self, Index):
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet1Value"] = deep_get(self.config.data,
                                                                                                       f"ResearchFarmingSetting.ResearchFarm{Index}Setting.EmotionValue")
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet2Value"] = 119

        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet1Record"] = datetime.now()
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet2Record"] = datetime.now()

        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Mode"] = deep_get(self.config.data,
                                                                                                f"ResearchFarmingSetting.ResearchFarm{Index}Setting.EmotionControlMethod")
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet1Control"] = deep_get(self.config.data,
                                                                                                         f"ResearchFarmingSetting.ResearchFarm{Index}Setting.Fleet1Control")
        self.config.modified[f"{self._GetResearchFarmTaskName(Index)}.Emotion.Fleet1Recover"] = deep_get(self.config.data,
                                                                                                         f"ResearchFarmingSetting.ResearchFarm{Index}Setting.Fleet1Recover")

    def _Call(self, Index):
        self.config.task_call(self._GetResearchFarmTaskName(Index))

    def run(self):
        for i in range(1, 7):
            if deep_get(self.config.data, f"ResearchFarmingSetting.ResearchFarm{i}Setting.Enable"):
                self._SetOilLimit(i)
                self._SetCampaign(i)
                self._SetFleet(i)
                self._SetEmotion(i)
                self._Call(i)
        self.config.Scheduler_Enable = False
        self.config.task_stop()
