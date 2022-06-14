import json
import shutil
import bagit


class Bagit:
    def __init__(self):
        self.subtype = 'bagit'

    def build(self, path: str, json_metadata: str):
        """
        Creates bagit package for given path
        :param path:
        :param json_metadata:
        :return:
        """
        print(json_metadata)
        metadata = json.loads(json_metadata.strip().replace("'", "\""))
        bag = bagit.make_bag(path, metadata)
        return bag.is_valid()

    def zipit(self, zip_name: str, path: str):
        """
        Zip all data
        :param zip_name:
        :param path:
        :return:
        """
        shutil.make_archive(zip_name.replace(".zip", ""), 'zip', path)
        return zip_name

    def validate(self, path: str):
        """
        Validate bagit
        :param path:
        :return:
        """
        bag = bagit.Bag(path)

        try:
            bag.validate()
            return True
        except bagit.BagValidationError as e:
            for d in e.details:
                if isinstance(d, bagit.ChecksumMismatch):
                    print("expected %s to have %s checksum of %s but found %s" %
                        (d.path, d.algorithm, d.expected, d.found))
        return False