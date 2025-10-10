from abc import ABC, abstractmethod


class TestSpec(ABC):
    def __init__(self, name, command):
        self.name = name
        self.command = command

    @abstractmethod
    def process_result(self, result):
        pass


class Test(TestSpec):
    def __init__(self):
        super().__init__("Test", "echo '{module_id} {fiber_endpoint} {session}'")

    def process_result(self, result):
        # Example processing: just print the result for now
        print(f"Processing result for {self.name}: {result}")


class CheckId(TestSpec):
    def __init__(self):
        super().__init__(
            "CheckId",
            "cd /home/thermal/BurnIn_moduleTest && python3 moduleTest.py --module {module_id} --slot `echo {fiber_endpoint} | perl -pe 's/.*OG//'` --board `echo {fiber_endpoint} | perl -pe 's/_.*//'` -c readOnlyID  --session {session}",
        )

    def process_result(self, result):
        # Example processing: just print the result for now
        print(f"Processing result for {self.name}: {result}")


class QuickTest(TestSpec):
    def __init__(self):
        super().__init__(
            "QuickTest",
            "cd /home/thermal/BurnIn_moduleTest && python3 moduleTest.py --module {module_id} --slot `echo {fiber_endpoint} | perl -pe 's/.*OG//'` --board `echo {fiber_endpoint} | perl -pe 's/_.*//'` -c PSquickTest  --session {session}",
        )

    def process_result(self, result):
        # Example processing: just print the result for now
        print(f"Processing result for {self.name}: {result}")


class FullTest(TestSpec):
    def __init__(self):
        super().__init__(
            "FullTest",
            "cd /home/thermal/BurnIn_moduleTest && python3 moduleTest.py --module {module_id} --slot `echo {fiber_endpoint} | perl -pe 's/.*OG//'` --board `echo {fiber_endpoint} | perl -pe 's/_.*//'` -c PSfullTest  --session {session}",
        )

    def process_result(self, result):
        # Example processing: just print the result for now
        print(f"Processing result for {self.name}: {result}")


class ConfigureOnly(TestSpec):
    def __init__(self):
        super().__init__(
            "ConfigureOnly",
            "cd /home/thermal/BurnIn_moduleTest && python3 moduleTest.py --module {module_id} --slot `echo {fiber_endpoint} | perl -pe 's/.*OG//'` --board `echo {fiber_endpoint} | perl -pe 's/_.*//'` -c configureonly  --session {session}",
        )

    def process_result(self, result):
        # Example processing: just print the result for now
        print(f"Processing result for {self.name}: {result}")


TEST_SPECS_MAP = {
    "Test": Test(),
    "CheckId": CheckId(),
    "QuickTest": QuickTest(),
    "FullTest": FullTest(),
    "ConfigureOnly": ConfigureOnly(),
}
