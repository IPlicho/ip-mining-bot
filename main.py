 if txt.startswith("-U "):
            parts = txt.split()
            if len(parts) == 3:
                uid = int(parts[1])
                amt = float(parts[2])
                current = user_balance.get(uid, 0.0)
                user_balance[uid] = max(0.0, current - amt)
                user_flow.setdefault(uid, []).append(f"-{amt:.2f} USDT  管理員扣除")
                bot.send_message(u, f"✅ -{amt:.2f} USDT → {uid}｜餘額：{user_balance[uid]:.2f}")
            return

        # 5. 派单 ID 金额
        if arr[0] == "派单" and len(arr) == 3:
            target = int(arr[1])
            amt = float(arr[2])
            global order_id
            oid = order_id
            order_id += 1
            orders[oid] = {"user": target, "amount": amt, "type": "assign", "status": 0}
            profit = round(amt * random.uniform(0.15, 0.20), 2)
            bot.send_message(u, f"✅ 派單成功｜#{oid} {amt} USDT → {target}")
            assign_notify = (
                f"📢 你有新派單\n"
                f"#{oid}\n"
                f"本金：{amt} USDT\n"
                f"預計利潤：+{profit} USDT"
            )
            mark = InlineKeyboardMarkup()
            mark.add(InlineKeyboardButton("接單", callback_data=f"acc_{oid}"))
            try:
                bot.send_message(target, assign_notify, reply_markup=mark)
            except Exception as e:
                print(f"通知用户派单失败: {e}")
            return

        # 6. 完成 订单号
        if arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            o["status"] = 2
            profit = o["amount"] * (random.uniform(0.15, 0.20) if o["type"] == "assign" else 0.05)
            user_balance[o["user"]] += o["amount"] + profit
            user_flow.setdefault(o["user"], []).append(f"+{profit:.2f} USDT  訂單#{oid}完成收益")
            bot.send_message(u, f"✅ 訂單 #{oid} 已完成，利潤已發放")
            return

        # 7. 取消订单 订单号
        if arr[0] == "取消订单" and len(arr) == 2:
            oid = int(arr[1])
            o = orders.get(oid)
            if not o:
                bot.send_message(u, "❌ 訂單不存在")
                return
            if o["status"] == 3:
                bot.send_message(u, "❌ 該訂單已取消")
                return
            if o["status"] == 1:
                user_balance[o["user"]] += o["amount"]
                user_flow.setdefault(o["user"], []).append(f"+{o['amount']:.2f} USDT  訂單#{oid}取消退款")
            o["status"] = 3
            bot.send_message(u, f"✅ 訂單 #{oid} 已取消，本金已退回")
            return

        # 8. 封ID 用户ID
        if arr[0] == "封ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned[target] = True
            bot.send_message(u, f"✅ 已封禁用戶 {target}")
            return

        # 9. 解ID 用户ID
        if arr[0] == "解ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned[target] = False
            bot.send_message(u, f"✅ 已解除用戶 {target} 的封禁")
            return

        bot.send_message(u, "❌ 指令格式：\n通过 ID\n查ID ID\n+U ID 金额\n-U ID 金额\n派单 ID 金额\n完成 订单号\n取消订单 订单号\n封ID ID\n解ID ID")
    except Exception as e:
        print(f"Admin cmd error: {e}")
        bot.send_message(u, "❌ 指令格式錯誤")

# ===================== 启动机器人 =====================
if __name__ == "__main__":
    threading.Thread(target=refresh_virtual_orders, daemon=True).start()
    threading.Thread(target=run_flask, daemon=True).start()
    print("✅ 機器人啟動成功，Railway防殺進程已開啟")
    bot.infinity_polling()
