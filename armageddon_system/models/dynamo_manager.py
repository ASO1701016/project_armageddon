from . import DynamoClass as db
from . import pay_log, qa, form, message

import hashlib


class DynamoManager():
    def get_pay_log_count(self):
        count = 0
        PayOffLog = db.PayOffLogsModel().scan()

        for item in PayOffLog:
            count += 1
        return count

    def get_pay_log_all(self):
        """
        精算記録を全件取得します。
        :rtype: list of map
        """

        all_pay_off_log = db.PayOffLogsModel.scan()
        return_items = []
        total = 0
        for item in all_pay_off_log:
            pay_log_form_list = []
            for form_item in item.PayOffLog.PayItems:
                pay_log_form_item = {
                    "pay_item_no": form_item.PayItemNo,
                    "form": form.Form(
                        form_name=form_item.FormName,
                        form_id=form_item.FormId,
                        fee=form_item.Fee,
                        issuance_days=None,
                        qr=None
                    ),
                    "quantity": form_item.Quantity,
                    "subtotal": int(form_item.Fee) * int(form_item.Quantity)
                }
                total += form_item.Fee * form_item.Quantity

                pay_log_form_list.append(pay_log_form_item)

            buyer_item = item.PayOffLog.Buyer
            buyer = {
                'student_id': buyer_item.BuyerNo,
                'school_id': buyer_item.SchoolId,
                'school_name': buyer_item.SchoolName,
                'course_id': buyer_item.CourseId,
                'course_name': buyer_item.CourseName,
            }
            pay_log_item = pay_log.PayLog(
                time_stamp=item.PayOffLog.Timestamp,
                # student_id=item.PayOffLog['Buyer']['BuyerNo'],
                student_id=buyer['student_id'],
                school_id=buyer['school_id'],
                school_name=buyer['school_name'],
                course_id=buyer['course_id'],
                course_name=buyer['course_name'],
                form_list=pay_log_form_list,

            )
            return_items.append(pay_log_item)
        return_items.sort(key=lambda x: x.time_stamp)
        return_items = list(reversed(return_items))
        return return_items, total

    def save_pay_log(self, pay_log: pay_log, id=False, IsPaid=False):
        """
        精算記録を保存します。
        :param pay_log: map
        :rtype: void
        """
        if id == False:
            all_pol = db.PayOffLogsModel().scan()
            count = 1
            for i in all_pol:
                count += 1
            id = count
        log = db.PayOffLogsModel(id)
        log.IsPaid = IsPaid
        buyer_info = {}
        pay_items = []
        count = 0
        total = 0
        for form_item in pay_log.form_list:
            count += 1
            fm = form_item['form']
            form_map = {
                'PayItemNo': count,
                'FormId': fm.form_id,
                'FormName': fm.form_name,
                'Fee': fm.fee,
                'Quantity': form_item['quantity']
            }
            total += fm.fee * form_item['quantity']
            pay_items.append(form_map)
        if pay_log.isStudent:
            buyer_info = {
                'BuyerNo': pay_log.student_id,
                'SchoolId': pay_log.school_id,
                'SchoolName': pay_log.school_name,
                'CourseId': pay_log.course_id,
                'CourseName': pay_log.course_name
            }
        else:
            buyer_info = {
                'BuyerName': pay_log.buyer_name,
                'BirthDay': pay_log.buyer_birth,
            }
        log.PayOffLog = {
            'Timestamp': pay_log.time_stamp,
            'Total': total,
            'Buyer': buyer_info,
            'PayItems': pay_items,
        }
        log.save()

    def del_pay_log(self, pay_log_id):
        """
        指定したIDの精算記録を削除します。
        :param pay_log_id: int
        :return: void
        """
        pay_log = db.PayOffLogsModel.get(hash_key=pay_log_id)
        pay_log.delete()

    def get_form_all(self, is_ascending=True):
        """
        精算項目を全件取得します。(通常はidで降順)
        is_ascending=Trueの場合昇順
        :rtype: all_form: list of map
        """
        all_form = db.FormsModel.scan()
        # pay_itemsの
        return_items = []
        for item in all_form:
            rt_form = form.Form(
                form_id=item.FormId,
                form_name=item.FormName,
                fee=item.Fee,
                issuance_days=item.IssuanceDays,
                qr=item.QR
            )
            return_items.append(rt_form)
        return_items.sort(key=lambda x: x.form_id)
        if not is_ascending:
            return_items = list(reversed(return_items))
        return return_items

    def save_form(self, form):
        """
        精算項目を保存します。
        :param pay_item: map
        :rtype: void
        """
        new_form = db.FormsModel(int(form['form_id']))
        # Formsの項目に埋め込む処理
        new_form.FormName = form['form_name']
        new_form.Fee = int(form['fee'])
        new_form.IssuanceDays = int(form['issuance_days'])
        new_form.QR = hashlib.md5(form['form_name'].encode()).hexdigest()
        new_form.save()

    def del_form(self, form_id):
        """
        指定したIDの精算項目を削除します。
        :param form_id:　int
        :rtype: void
        """
        fm = db.FormsModel
        form_item = fm.get(hash_key=int(form_id))
        form_item.delete()

    def get_qa_all(self):
        """
        QAを全件取得します。
        :rtype: list of map
        """
        all_qa = db.QuestionAndAnswersModel.scan()
        # QAに埋め込む処理
        qa_list = []
        for item in all_qa:
            question = item.Questions
            answer = item.Answer
            rt_qa = qa.QA(
                qa_id=item.QuestionAndAnswerId,
                question=question,
                answer=answer
            )
            qa_list.append(rt_qa)

        return qa_list

    def save_qa(self, qa):
        """
        QAを保存します。
        :param qa:list of map
        :rtype: void
        """
        qa_item = db().QuestionAndAnswersModel(int(qa['qa_id']))
        qa_item.Questions = qa['questions']
        qa_item.Answer = qa['answer']
        qa_item.save()

    def del_qa(self, qa_id):
        """
        指定したIDのQAを削除します。
        :param qa_id: int
        :rtype: void
        """
        qa = db.QuestionAndAnswersModel.get(int(qa_id))
        qa.delete()

    def get_next_qa_id(self):
        all_qa = db.QuestionAndAnswersModel.scan()
        max_id = 0
        for i in all_qa:
            max_id = max(max_id, i.QuestionAndAnswerId)
        return max_id + 1

    def get_next_message_id(self):
        all_message = db.MessagesModel.scan()
        max_id = 0
        for i in all_message:
            max_id = max(max_id, i.MessageId)
        return max_id + 1

    def get_next_form_id(self):
        all_form = db.FormsModel.scan()
        max_id = 0
        for i in all_form:
            max_id = max(max_id, i.FormId)
        return max_id + 1

    def get_qa(self, qa_id):
        """
        qa_idを渡して対象のQAを取得
        """
        qam = db.QuestionAndAnswersModel(qa_id)
        qa_item = qa.QA(
            qa_id=qam.QuestionAndAnswerId,
            question=qam.Questions,
            answer=qam.Answer
        )
        return qa_item

    def get_message_list(self):
        """
        LINE Botのメッセージを全件取得します。
        :rtype: list of map
        """
        message_list = db.MessagesModel.scan()
        messages = []
        # print(message_list)
        # messageを埋め込む処理
        for item in message_list:
            # item.Message['Timestamp'] = datetime.datetime.strftime(ite.Message['Timestamp'], '%Y-%m-%d')
            # item.Message['Timestamp'] = item.Message['Timestamp'].isoformat()
            # print(item.Message['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'))
            # item.Message['Timestamp'] = item.Message['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            messages.append(dict(item))
        return messages

    def get_message(self, message_id):
        """
        LINE Botのメッセージを全件取得します。
        :rtype: list of map
        """
        message = db.MessagesModel.get(int(message_id))
        # print(dict(message))
        # messageを埋め込む処理
        return message

    def save_message_list(self, message):
        """
        LINE Botのメッセージを保存します。
        :param bot_message: map
        :rtype: void
        """
        new_message = db.MessagesModel(int(message['message_id']))
        import datetime
        new_message.Message = {
            'MessageContent': message['message'],
            'ImagePath': message['image'],
            'Timestamp': datetime.datetime.strptime(message['time_stamp'], '%Y-%m-%d')
        }
        new_message.save()

    def del_message_list(self, bot_message_id):
        """
        指定したIDのLINE Bot メッセージを削除します。
        :param bot_message_id: int
        :rtype: void
        """
        message = db.MessagesModel(int(bot_message_id))
        message.delete()

    def check_login_id(self, user_id, user_pass):
        """
        ユーザIDとパスワードからログイン可否します。
        :param user_id: str
        :param user_pass: str
        :rtype: bool
        """
        try:
            user = db.UsersModel.get(user_id)
            if user.Password == user_pass:
                return True
            else:
                return False
        except Exception as e:
            return False
