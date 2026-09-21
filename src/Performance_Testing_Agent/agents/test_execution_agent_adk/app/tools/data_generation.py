import csv
import json
import os
import random
import uuid

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GENERATED_DATA_DIR = "generated_data"


class TestDataGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate(
        self,
        data_type,
        count,
        output_format="csv",
        requirements="",
    ) -> dict:

        os.makedirs(GENERATED_DATA_DIR, exist_ok=True)

        data_type = data_type.lower().strip()
        output_format = output_format.lower().strip()

        if count < 1:
            return {
                "status": "error",
                "message": "Data count must be greater than zero.",
            }

        if output_format not in {"csv", "json"}:
            return {
                "status": "error",
                "message": "Supported formats are CSV and JSON.",
            }

        # LLM is used ONLY to determine the schema.
        schema = self._determine_schema(
            data_type=data_type,
            requirements=requirements,
        )

        if not schema:
            return {
                "status": "error",
                "message": "Unable to determine a valid data schema.",
            }

        # Records are generated locally in Python.
        records = self._generate_records(
            schema=schema,
            count=count,
        )

        file_name = (
            f"{data_type}_{uuid.uuid4().hex[:8]}"
            f".{output_format}"
        )

        file_path = os.path.join(
            GENERATED_DATA_DIR,
            file_name,
        )

        if output_format == "csv":
            self._write_csv(
                file_path=file_path,
                records=records,
                schema=schema,
            )
        else:
            self._write_json(
                file_path=file_path,
                records=records,
            )

        # Validate the generated artifact.
        validation_result = self._validate_artifact(
            file_path=file_path,
            output_format=output_format,
            schema=schema,
            expected_count=count,
        )

        if validation_result["status"] != "success":
            return {
                "status": "error",
                "message": "Generated test-data artifact failed validation.",
                "validation": validation_result,
                "file_path": file_path,
            }

        return {
            "status": "success",
            "message": "Synthetic test data generated successfully.",
            "data_type": data_type,
            "record_count": count,
            "output_format": output_format,
            "file_name": file_name,
            "file_path": file_path,
            "schema": schema,
            "validation": validation_result,
        }

    def _determine_schema(self, data_type, requirements):

        prompt = f"""
You are an expert performance-testing data engineer.

Determine a practical schema for synthetic test data.

Data type:
{data_type}

Additional requirements:
{requirements}

Return ONLY valid JSON containing a list of field names.

Example:
["customer_id", "name", "email", "account_number"]

Do not generate records.
Do not provide explanations.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.1,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You design schemas for synthetic "
                        "performance-testing data."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        content = response.choices[0].message.content

        if not content:
            return self._fallback_schema(data_type)

        content = content.strip()

        if content.startswith("```"):
            first_newline = content.find("\n")

            if first_newline != -1:
                content = content[first_newline + 1:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            schema = json.loads(content)

            if not isinstance(schema, list):
                raise ValueError

            if not schema:
                raise ValueError

            if not all(
                isinstance(field, str) and field.strip()
                for field in schema
            ):
                raise ValueError

            return schema

        except (json.JSONDecodeError, ValueError):
            return self._fallback_schema(data_type)

    @staticmethod
    def _fallback_schema(data_type):

        schemas = {
            "customers": [
                "customer_id",
                "name",
                "email",
                "phone",
                "account_number",
            ],
            "transactions": [
                "transaction_id",
                "account_number",
                "transaction_type",
                "amount",
                "currency",
            ],
            "credentials": [
                "username",
                "password",
            ],
            "test_accounts": [
                "account_number",
                "account_type",
                "customer_name",
                "balance",
            ],
        }

        return schemas.get(
            data_type,
            [
                "record_id",
                "name",
                "value",
            ],
        )

    @staticmethod
    def _generate_records(schema, count):

        records = []

        for index in range(count):

            record = {}

            for field in schema:

                field_lower = field.lower()

                if "id" in field_lower:
                    value = str(uuid.uuid4())

                elif "email" in field_lower:
                    value = f"user{index + 1}@example.com"

                elif "phone" in field_lower:
                    value = (
                        "9"
                        + "".join(
                            random.choice("0123456789")
                            for _ in range(9)
                        )
                    )

                elif "name" in field_lower:
                    value = f"Test User {index + 1}"

                elif "account" in field_lower:
                    value = (
                        "AC"
                        + str(1000000000 + index)
                    )

                elif "username" in field_lower:
                    value = f"testuser{index + 1}"

                elif "password" in field_lower:
                    value = f"Test@{100000 + index}"

                elif "amount" in field_lower:
                    value = round(
                        random.uniform(100, 100000),
                        2,
                    )

                elif "currency" in field_lower:
                    value = "INR"

                elif "transaction" in field_lower:
                    value = random.choice(
                        [
                            "UPI",
                            "NEFT",
                            "IMPS",
                            "RTGS",
                        ]
                    )

                elif "balance" in field_lower:
                    value = round(
                        random.uniform(1000, 500000),
                        2,
                    )

                elif "type" in field_lower:
                    value = "TEST"

                else:
                    value = f"test_value_{index + 1}"

                record[field] = value

            records.append(record)

        return records

    @staticmethod
    def _write_csv(file_path, records, schema):

        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as data_file:

            writer = csv.DictWriter(
                data_file,
                fieldnames=schema,
            )

            writer.writeheader()
            writer.writerows(records)

    @staticmethod
    def _write_json(file_path, records):

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as data_file:

            json.dump(
                records,
                data_file,
                indent=2,
            )

    @staticmethod
    def _validate_artifact(
        file_path,
        output_format,
        schema,
        expected_count,
    ):

        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": "Generated data file does not exist.",
            }

        try:

            if output_format == "csv":

                with open(
                    file_path,
                    "r",
                    newline="",
                    encoding="utf-8",
                ) as data_file:

                    reader = csv.DictReader(data_file)

                    actual_schema = reader.fieldnames

                    if actual_schema != schema:
                        return {
                            "status": "error",
                            "message": "CSV schema does not match expected schema.",
                            "expected_schema": schema,
                            "actual_schema": actual_schema,
                        }

                    records = list(reader)

                actual_count = len(records)

            elif output_format == "json":

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                ) as data_file:

                    records = json.load(data_file)

                if not isinstance(records, list):
                    return {
                        "status": "error",
                        "message": "JSON artifact must contain a list of records.",
                    }

                actual_count = len(records)

                for index, record in enumerate(records):

                    if not isinstance(record, dict):
                        return {
                            "status": "error",
                            "message": (
                                f"JSON record {index + 1} "
                                "is not an object."
                            ),
                        }

                    if list(record.keys()) != schema:
                        return {
                            "status": "error",
                            "message": (
                                f"JSON schema mismatch at "
                                f"record {index + 1}."
                            ),
                            "expected_schema": schema,
                            "actual_schema": list(record.keys()),
                        }

            else:
                return {
                    "status": "error",
                    "message": (
                        f"Unsupported validation format: "
                        f"{output_format}"
                    ),
                }

            if actual_count != expected_count:
                return {
                    "status": "error",
                    "message": "Record count does not match requested count.",
                    "expected_count": expected_count,
                    "actual_count": actual_count,
                }

            return {
                "status": "success",
                "message": "Artifact validation passed.",
                "schema_valid": True,
                "record_count_valid": True,
                "expected_count": expected_count,
                "actual_count": actual_count,
                "format": output_format,
            }

        except (OSError, json.JSONDecodeError, csv.Error) as exc:

            return {
                "status": "error",
                "message": "Unable to validate generated artifact.",
                "error": str(exc),
            }


def generate_test_data(
    data_type,
    count,
    output_format="csv",
    requirements="",
) -> dict:

    generator = TestDataGenerator()

    return generator.generate(
        data_type=data_type,
        count=count,
        output_format=output_format,
        requirements=requirements,
    )